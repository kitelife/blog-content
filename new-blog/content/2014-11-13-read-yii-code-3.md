Title: Yii源码阅读笔记 - 组件集成
Date: 2014-11-13
Author: youngsterxyf
Slug: read-yii-code-3
Tags: PHP, Yii, 笔记, 总结

### 概述

Yii框架将各种功能封装成组件，使用时按需配置加载，从而提高应用的性能。内置的组件又分为核心组件与非核心组件，核心组件是任何Web应用和Console应用都需要的。
此外，应用开发者还可以按照一定规则封装配置使用自己的功能组件。Yii会把应用需要的组件都加载到应用容器`Yii::app()`中，使得组件的使用方式一致方便。

基于Yii框架开发应用需要理解如何配置组件、如何开发自己的组件，对应着需要理解Yii是如何注册加载组件的。


### 分析

从[Yii源码阅读笔记 - 请求处理基本流程](http://youngsterxyf.github.io/2014/11/04/read-yii-code-1/)一文可知，Yii加载组件的入口为抽象类CApplication构造方法中的以下两行代码：

    :::php
    $this->registerCoreComponents();
    $this->configure($config);
    
------

`registerCoreComponents`方法定义于类CWebApplication中，用于加载Web应用的核心组件，组件列表如下：

    :::php
    array(
        // 核心组件
        'coreMessages'=>array(
            'class'=>'CPhpMessageSource',
            'language'=>'en_us',
            'basePath'=>YII_PATH.DIRECTORY_SEPARATOR.'messages',
        ),
        'db'=>array(
            'class'=>'CDbConnection',
        ),
        'messages'=>array(
            'class'=>'CPhpMessageSource',
        ),
        'errorHandler'=>array(
            'class'=>'CErrorHandler',
        ),
        'securityManager'=>array(
            'class'=>'CSecurityManager',
        ),
        'statePersister'=>array(
            'class'=>'CStatePersister',
        ),
        'urlManager'=>array(
            'class'=>'CUrlManager',
        ),
        'request'=>array(
            'class'=>'CHttpRequest',
        ),
        'format'=>array(
            'class'=>'CFormatter',
        ),
        
        // 以下是Web应用额外需要的核心组件
        'session'=>array(
            'class'=>'CHttpSession',
        ),
        'assetManager'=>array(
            'class'=>'CAssetManager',
        ),
        'user'=>array(
            'class'=>'CWebUser',
        ),
        'themeManager'=>array(
            'class'=>'CThemeManager',
        ),
        'authManager'=>array(
            'class'=>'CPhpAuthManager',
        ),
        'clientScript'=>array(
            'class'=>'CClientScript',
        ),
        'widgetFactory'=>array(
            'class'=>'CWidgetFactory',
        ),
    )
    
注册加载组件都是直接调用方法`setComponents`，间接调用方法`setComponent`来完成的。

------

`configure`方法定义于类`CModule`中，是用于加载所有配置信息的，实现如下：

    :::php
    public function configure($config)
    {
        if(is_array($config))
        {
            foreach($config as $key=>$value)
                $this->$key=$value;
        }
    }

从[Yii源码阅读笔记 - 请求处理基本流程](http://youngsterxyf.github.io/2014/11/04/read-yii-code-1/)一文可知，配置信息的加载是基于类`CComponent`中的魔术方法`__set`来完成的，该方法实现如下：

    :::php
    public function __set($name,$value)
    {
        // PHP的类名、函数名、方法名都是不区分大小写的！
        $setter='set'.$name;
        if(method_exists($this,$setter))
            return $this->$setter($value);
        elseif(strncasecmp($name,'on',2)===0 && method_exists($this,$name))
        {
            // duplicating getEventHandlers() here for performance
            $name=strtolower($name);
            if(!isset($this->_e[$name]))
                $this->_e[$name]=new CList;
            return $this->_e[$name]->add($value);
        }
        elseif(is_array($this->_m))
        {
            foreach($this->_m as $object)
            {
                if($object->getEnabled() && (property_exists($object,$name) || $object->canSetProperty($name)))
                    return $object->$name=$value;
            }
        }
        if(method_exists($this,'get'.$name))
            throw new CException(Yii::t('yii','Property "{class}.{property}" is read only.',
                array('{class}'=>get_class($this), '{property}'=>$name)));
        else
            throw new CException(Yii::t('yii','Property "{class}.{property}" is not defined.',
                array('{class}'=>get_class($this), '{property}'=>$name)));
    }

而类CModule中又定义了方法`setComponents`，所以对于key为`components`的配置项，也是调用方法`setComponents`，间接调用方法`setComponent`来完成的。

方法`setComponent`实现如下：

    :::php
    /**
     * Puts a component under the management of the module.
     * The component will be initialized by calling its {@link CApplicationComponent::init() init()}
     * method if it has not done so.
     * @param string $id component ID
     * @param array|IApplicationComponent $component application component
     * (either configuration array or instance). If this parameter is null,
     * component will be unloaded from the module.
     * @param boolean $merge whether to merge the new component configuration
     * with the existing one. Defaults to true, meaning the previously registered
     * component configuration with the same ID will be merged with the new configuration.
     * If set to false, the existing configuration will be replaced completely.
     * This parameter is available since 1.1.13.
     */
    public function setComponent($id,$component,$merge=true)
    {
        if($component===null)
        {
            unset($this->_components[$id]);
            return;
        }
        elseif($component instanceof IApplicationComponent)
        {
            $this->_components[$id]=$component;

            if(!$component->getIsInitialized())
                $component->init();

            return;
        }
        elseif(isset($this->_components[$id]))
        {
            if(isset($component['class']) && get_class($this->_components[$id])!==$component['class'])
            {
                unset($this->_components[$id]);
                $this->_componentConfig[$id]=$component; //we should ignore merge here
                return;
            }

            foreach($component as $key=>$value)
            {
                if($key!=='class')
                    $this->_components[$id]->$key=$value;
            }
        }
        // 以configure方法为入口的组件注册可能走的分支
        elseif(isset($this->_componentConfig[$id]['class'],$component['class'])
            && $this->_componentConfig[$id]['class']!==$component['class'])
        {
            $this->_componentConfig[$id]=$component; //we should ignore merge here
            return;
        }

        // 以configure方法为入口的组件注册可能走的分支
        if(isset($this->_componentConfig[$id]) && $merge)
            // 对组件的信息进行合并，即意味着如果是对核心组件做额外配置，可以不用指定class等信息。
            $this->_componentConfig[$id]=CMap::mergeArray($this->_componentConfig[$id],$component);
        else
            // 核心组件注册全走这个分支
            // 非核心组件、自定义组件注册走这个分支
            $this->_componentConfig[$id]=$component;
    }

对于以registerCoreComponents方法、configure方法为入口的组件注册，调用setComponent方法时的参数$component是一个数组。

注册核心组件前，应用对象的属性`_component`和`_componentConfig`都为空，所以核心组件注册最终走的都是**最后一个else分支**。

由于可以配置与核心组件相同ID的组件，比如db，那么注册配置的组件（以configure方法为入口）走的是**最后一个elseif分支或者最后一个if分支**。

可以看到以这两个方法为入口的组件注册都没有对组件进行初始化。那么什么时候初始化组件的呢？只能是调用组件的时候了。

------

组件是通过应用对象容器来调用的。以db组件为例，调用方式为：`Yii::app()->db`，但实际是基于魔术方法`__get`来完成的，该魔术方法定义于类CModule中，实现如下：

    :::php
    public function __get($name)
    {
        if($this->hasComponent($name))
            return $this->getComponent($name);
        else
            return parent::__get($name);
    }

先尝试查找对应$name的组件。从这里可以看出Web应用容器中除了存组件，还可以存其他信息，如所有的配置信息。

方法hasComponent实现如下：

    :::php
    public function hasComponent($id)
    {
        return isset($this->_components[$id]) || isset($this->_componentConfig[$id]);
    }
    
之所以会先查看属性_components，是因为_components中保存的组件是已经加载好的，而_componentConfig保存的是所有注册的组件，但未初始化。即_components中的组件是_componentConfig中组件的子集，检测起来会更快？我的理解是这样的。
    
方法getComponent实现如下：

    :::php
    public function getComponent($id,$createIfNull=true)
    {
        if(isset($this->_components[$id]))
            return $this->_components[$id];
        elseif(isset($this->_componentConfig[$id]) && $createIfNull)
        {
            $config=$this->_componentConfig[$id];
            if(!isset($config['enabled']) || $config['enabled'])
            {
                Yii::trace("Loading \"$id\" application component",'system.CModule');
                unset($config['enabled']);
                $component=Yii::createComponent($config);
                $component->init();
                return $this->_components[$id]=$component;
            }
        }
    }

先查看属性_components中是否已保存初始化好的对应组件，是，则直接取出来返回，这样重复调用相同组件只会初始化一次；否，则对该组件进行初始化。

组件初始化分为两个步骤：

1. Yii根据组件的配置信息实例化一个组件对象，即`$component=Yii::createComponent($config)`
2. 组件对象调用自己的方法`init`完成一些初始化操作，即`$component->init()`

初始化结束后，将组件对象存入属性_components中。

------

静态方法`createComponent`定义于类YiiBase中，实现如下：

    :::php
    /**
     * Creates an object and initializes it based on the given configuration.
     *
     * The specified configuration can be either a string or an array.
     * If the former, the string is treated as the object type which can
     * be either the class name or {@link YiiBase::getPathOfAlias class path alias}.
     * If the latter, the 'class' element is treated as the object type,
     * and the rest of the name-value pairs in the array are used to initialize
     * the corresponding object properties.
     *
     * Any additional parameters passed to this method will be
     * passed to the constructor of the object being created.
     *
     * @param mixed $config the configuration. It can be either a string or an array.
     * @return mixed the created object
     * @throws CException if the configuration does not have a 'class' element.
     */
    public static function createComponent($config)
    {
        // 如果传入的组件配置信息是字符串类型，则认为是对象类型
        if(is_string($config))
        {
            $type=$config;
            $config=array();
        }
        // 如果是数组，则必须指定组件所对应的class
        elseif(isset($config['class']))
        {
            $type=$config['class'];
            unset($config['class']);
        }
        else
            throw new CException(Yii::t('yii','Object configuration must be an array containing a "class" element.'));

        // 如果组件所对应的类型还没加载，则加载进来
        if(!class_exists($type,false))
            $type=Yii::import($type,true);

        // 如果除了$config，还传递了其他参数，则根据额外的参数来实例化。对于组件初始化来说，不会走这个分支
        if(($n=func_num_args())>1)
        {
            $args=func_get_args();
            if($n===2)
                $object=new $type($args[1]);
            elseif($n===3)
                $object=new $type($args[1],$args[2]);
            elseif($n===4)
                $object=new $type($args[1],$args[2],$args[3]);
            else
            {
                unset($args[0]);
                $class=new ReflectionClass($type);
                // Note: ReflectionClass::newInstanceArgs() is available for PHP 5.1.3+
                // $object=$class->newInstanceArgs($args);
                $object=call_user_func_array(array($class,'newInstance'),$args);
            }
        }
        // 没有额外的参数，则直接实例化组件
        else
            $object=new $type;

        // $config中除了class外的其他字段都作为组件对象的属性进行赋值
        foreach($config as $key=>$value)
            $object->$key=$value;

        return $object;
    }

从上述代码可以看出，在配置组件时，如果是配置核心组件，可以不提供class字段，否则一定要提供。除了class字段，还可以为组件对象的属性赋值。按照PHP中对一个对象的属性进行赋值的规则：

1. 如果该对象有public的该属性，则直接赋值
2. 否则看该对象所在继承树上是否有定义魔术方法`__set`，如果有则调用`__set`来处理赋值过程
3. 如果连`__set`也没有，则为该对象生成一个public的属性，然后赋值给它

可以将自定义组件类需要初始化赋值的属性：

1. 定义为public访问控制
2. 如果非public，则应该魔术方法`__set`
3. 也可以不定义该属性（我觉得还是定义一下比较好，否则不好理解）

------

在静态方法createComponent返回组件对象后，接着调用组件对象自身的init方法来完成一些初始化工具。这也就意味着自定义组件需要有init方法。

从核心组件的定义可以看到，组件应该继承自抽象类`CApplicationComponent`（见文件`yii/framework/base/CApplicationComponent.php`）。该类定义了方法init和getIsInitialized。
自定义组件继承自`CApplicationComponent`，若没有额外的初始化操作，也可以不再定义自己的init方法。如果定义自己的init方法，最好也间接调用一下父类的init方法（`parent::init()`），
从而避免一些可能潜在的兼容问题。

关于自定义组件的更多具体细节，可以参考[基于socket.io的实时消息推送](http://youngsterxyf.github.io/2014/09/06/socket.io-push-server/)一文中的示例。