Title: Yii源码阅读笔记 - 缓存
Date: 2014-11-19
Author: youngsterxyf
Slug: read-yii-code-6
Tags: PHP, Yii, 笔记, 总结


### 概述

从之前的文章[Yii源码阅读笔记 - 路由解析](http://youngsterxyf.github.io/2014/11/12/read-yii-code-2/)
及[Yii源码阅读笔记 - Model层实现](http://youngsterxyf.github.io/2014/11/14/read-yii-code-4/)可以看到Yii框架对于**解析好的路由规则**及**数据表的schema**都会根据条件尝试读写缓存
来提高应用性能。

但缓存组件并非核心组件，需要额外的配置，默认ID为`cache`，如果不使用该ID，那么就得注意同时配置好框架中使用缓存的组件。

恰当地使用缓存组件，能明显地提高应用的性能。

针对不同的缓存后端（backend），Yii框架提供了多种缓存组件，如文件缓存（CFileCache）、Memcached缓存（CMemCache）、Redis缓存（CRedisCache）等。这些缓存组件（除CDummyCache外，CDummyCache并不是一个有效的缓存组件）均直接继承自抽象类CCache（见文件`yii/framework/caching/CCache.php`）。

下面以使用Memcached缓存为例，分析Yii框架缓存组件的实现。

### 分析

类`CMemcache`所在的整个继承树（`CMemcache` -> `CCache` -> `CApplicationComponent` -> `CComponent`）上的类都没有构造方法。

`CMemcache`的init方法实现如下：

    :::php
    public function init()
    {
        // 调用父类CCache的init方法
        parent::init();
        // 获取配置的Memcached服务器列表
        $servers=$this->getServers();
        // 获取一个Memcache或Memcached对象
        $cache=$this->getMemCache();
        if(count($servers))
        {
            // 将配置的Memcached服务器加到池中
            foreach($servers as $server)
            {
                // 可选择使用memcached php扩展，但最好别这样，因为memcached扩展不支持一些有用的配置选项，从addServer方法的参数列表就可以看出
                // memcached扩展默认使用余数分步哈希算法，但可配置使用一致性哈希算法
                // 应使用memcache扩展
                if($this->useMemcached)
                    $cache->addServer($server->host,$server->port,$server->weight);
                else
                    $cache->addServer($server->host,$server->port,$server->persistent,$server->weight,$server->timeout,$server->retryInterval,$server->status);
            }
        }
        // 如果没有配置服务器列表，则默认使用localhost:11211
        else
            $cache->addServer('localhost',11211);
    }

其中调用的父类的init方法实现如下：

    :::php
    public function init()
    {
        parent::init();
        // 可以为整个应用的缓存的key加一个统一的前缀，这是为了避免在同一个缓存池中，不同应用的key冲突
        if($this->keyPrefix===null)
            // 如果没有配置keyPrefix，则以应用的id作为keyPrefix，这个key，可以配置，如果未配置，则`sprintf('%x',crc32($this->getBasePath().$this->name))`这样生成，
            // 其中name表示应用的名称，可配置，默认为“My Application”
            // getId方法定义于抽象类CApplication中
            $this->keyPrefix=Yii::app()->getId();
    }

`CMemcache`的init方法中调用的方法`getServers`和`getMemcache`，实现如下所示：

    :::php
    public function getMemCache()
    {
        // 单例
        if($this->_cache!==null)
            return $this->_cache;
        else
        {
            // 还是用memcache吧
            $extension=$this->useMemcached ? 'memcached' : 'memcache';
            // 检测一下是否记载了所需扩展
            if(!extension_loaded($extension))
                throw new CException(Yii::t('yii',"CMemCache requires PHP {extension} extension to be loaded.",
                    array('{extension}'=>$extension)));
            // 实例化
            return $this->_cache=$this->useMemcached ? new Memcached : new Memcache;
        }
    }
    
    public function getServers()
    {
        return $this->_servers;
    }

与`getServers`对应的有方法`setServers`，如果需要配置缓存服务器列表，则应该为缓存组件配置`servers`一项，基本形式为：

    :::php
    'servers'=>array(
        array(
            'host'=>'127.0.0.1',
            'port'=>11211,
        ),
    ),

`setServers`方法实现如下：

    :::php
    public function setServers($config)
    {
        foreach($config as $c)
            $this->_servers[]=new CMemCacheServerConfiguration($c);
    }

其中实例化的类`CMemCacheServerConfiguration`也定义于文件`yii/framework/caching/CMemCache.php`中，其构造方法实现如下：

    :::php
    public function __construct($config)
    {
        if(is_array($config))
        {
            foreach($config as $key=>$value)
                $this->$key=$value;
            if($this->host===null)
                throw new CException(Yii::t('yii','CMemCache server configuration must have "host" value.'));
        }
        else
            throw new CException(Yii::t('yii','CMemCache server configuration must be an array.'));
    }

从该构造方法可以看到该类的作用就是将一个Memcached缓存服务器的配置信息封装成一个配置类对象。该类有如下public的属性：

    :::php
    /**
     * @var string memcache server hostname or IP address
     */
    public $host;
    /**
     * @var integer memcache server port
     */
    public $port=11211;
    /**
     * @var boolean whether to use a persistent connection
     */
    public $persistent=true;
    /**
     * @var integer probability of using this server among all servers.
     */
    public $weight=1;
    /**
     * @var integer value in seconds which will be used for connecting to the server
     */
    public $timeout=15;
    /**
     * @var integer how often a failed server will be retried (in seconds)
     */
    public $retryInterval=15;
    /**
     * @var boolean if the server should be flagged as online upon a failure
     */
    public $status=true;

这些属性也即是每台缓存服务器的可配置项，当然如果用的是memcached扩展，某些配置项就用不上了。

------

类`CCache`定义了访问控制类型public的方法`get`、`mget`、`set`、`add`、`delete`、`flush`，对应Yii框架缓存组件提供的几个操作，即开发者可以使用这些方法来操作缓存。

    :::php
    // 根据单个key，获取对应的value
    public function get($id)
    {
        // generateUniqueKey是根据$id来生成一个唯一的key，也即真正存到缓存的key并不是get方法的$id参数值
        $value = $this->getValue($this->generateUniqueKey($id));
        // 如果设置为不进行序列化，则直接返回取得的值
        if($value===false || $this->serializer===false)
            return $value;
        // 如果未设置serializer，则说明存储时使用的是默认的序列化方法，取到数据后对应地需要使用默认的方法进行反序列化
        if($this->serializer===null)
            $value=unserialize($value);
        else
            // 否则，使用指定的方法进行反序列化
            $value=call_user_func($this->serializer[1], $value);
        if(is_array($value) && (!$value[1] instanceof ICacheDependency || !$value[1]->getHasChanged()))
        {
            Yii::trace('Serving "'.$id.'" from cache','system.caching.'.get_class($this));
            return $value[0];
        }
        else
            return false;
    }
    
    // 根据多个key值（$ids），获取多个value
    public function mget($ids)
    {
        $uids = array();
        foreach ($ids as $id)
            $uids[$id] = $this->generateUniqueKey($id);

        $values = $this->getValues($uids);
        $results = array();
        if($this->serializer === false)
        {
            foreach ($uids as $id => $uid)
                $results[$id] = isset($values[$uid]) ? $values[$uid] : false;
        }
        else
        {
            foreach($uids as $id => $uid)
            {
                $results[$id] = false;
                if(isset($values[$uid]))
                {
                    $value = $this->serializer === null ? unserialize($values[$uid]) : call_user_func($this->serializer[1], $values[$uid]);
                    if(is_array($value) && (!$value[1] instanceof ICacheDependency || !$value[1]->getHasChanged()))
                    {
                        Yii::trace('Serving "'.$id.'" from cache','system.caching.'.get_class($this));
                        $results[$id] = $value[0];
                    }
                }
            }
        }
        return $results;
    }
    
    // 向$id存储一个元素值为 $value
    public function set($id,$value,$expire=0,$dependency=null)
    {
        Yii::trace('Saving "'.$id.'" to cache','system.caching.'.get_class($this));

        if ($dependency !== null && $this->serializer !== false)
            $dependency->evaluateDependency();

        if ($this->serializer === null)
            $value = serialize(array($value,$dependency));
        elseif ($this->serializer !== false)
            $value = call_user_func($this->serializer[0], array($value,$dependency));

        return $this->setValue($this->generateUniqueKey($id), $value, $expire);
    }
    
    // 在缓存服务器之前不存在$id时， 以id作为key存储一个变量$value到缓存服务器
    public function add($id,$value,$expire=0,$dependency=null)
    {
        Yii::trace('Adding "'.$id.'" to cache','system.caching.'.get_class($this));

        if ($dependency !== null && $this->serializer !== false)
            $dependency->evaluateDependency();

        if ($this->serializer === null)
            $value = serialize(array($value,$dependency));
        elseif ($this->serializer !== false)
            $value = call_user_func($this->serializer[0], array($value,$dependency));

        return $this->addValue($this->generateUniqueKey($id), $value, $expire);
    }
    
    // 根据id删除缓存项
    public function delete($id)
    {
        Yii::trace('Deleting "'.$id.'" from cache','system.caching.'.get_class($this));
        return $this->deleteValue($this->generateUniqueKey($id));
    }
    
    // 清空缓存
    public function flush()
    {
        Yii::trace('Flushing cache','system.caching.'.get_class($this));
        return $this->flushValues();
    }

从上述代码中可以看到，每种操作方法实际上都是调用另一个方法来完成操作：

- get -> getValue
- mget -> getValues
- set -> setValue
- add -> addValue
- delete -> deleteValue
- flush -> flushValues

但抽象类`CCache`中对于后面的这些方法并没有真正实现操作逻辑（除了getValues，其实现是循环调用getValue，也许并不是开发者想要的实现，`CMemCache`类重写了这个方法），需要在继承类中实现。`CMemCache`类中对这些方法实现如下：

    :::php
    protected function getValue($key)
    {
        return $this->_cache->get($key);
    }
    
    protected function getValues($keys)
    {
        return $this->useMemcached ? $this->_cache->getMulti($keys) : $this->_cache->get($keys);
    }
    
    protected function setValue($key,$value,$expire)
    {
        // 注意：这个地方对于开发者来说也许是个坑
        // 该方法的参数$expire并不是一个时间点，而是一个时间间隔
        // $expire = 0表示不会超时失效
        if($expire>0)
            $expire+=time();
        else
            $expire=0;
        
        // 使用memcache扩展时，add方法的那个额外参数值0，对应参数flag，表示是否对数据使用zlib进行压缩
        return $this->useMemcached ? $this->_cache->set($key,$value,$expire) : $this->_cache->set($key,$value,0,$expire);
    }
    
    protected function addValue($key,$value,$expire)
    {
        if($expire>0)
            $expire+=time();
        else
            $expire=0;

        return $this->useMemcached ? $this->_cache->add($key,$value,$expire) : $this->_cache->add($key,$value,0,$expire);
    }
    
    protected function deleteValue($key)
    {
        return $this->_cache->delete($key, 0);
    }
    
    protected function flushValues()
    {
        return $this->_cache->flush();
    }

