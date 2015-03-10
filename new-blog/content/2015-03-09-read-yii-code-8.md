Title: Yii源码阅读笔记 - 日志组件
Date: 2015-03-09
Author: youngsterxyf
Slug: read-yii-code-8
Tags: PHP, Yii, 笔记, 总结


### 使用

Yii框架为开发者提供两个静态方法进行日志记录：

    :::php
    <?php
    Yii::log($message, $level, $category);
    Yii::trace($message, $category);

两者的区别在于后者依赖于应用开启调试模式，即定义常量YII_DEBUG：

    :::php
    <?php
    defined('YII_DEBUG') or define('YII_DEBUG', true);

Yii::log方法的调用需要指定message的level和category。category是格式为“xxx.yyy.zzz”的路径别名字符串，比如日志是在yii/framework/web/CController类中记录的，那么category为“system.web.CController”。level应为以下几种之一：

- trace：Yii::trace方法即是使用的这个level。用于跟踪执行流
- info：记录通用信息日志
- profile：用于性能分析
- warning：用于记录警告日志
- error：用于记录重大错误日志

要想日志真的输出到文件、邮件、web页面等地方，还得为应用添加如下配置：

    :::php
    <?php
    array(
        ......
        'preload'=>array('log'),
        'components'=>array(
            ......
            'log'=>array(
                'class'=>'CLogRouter',
                'routes'=>array(
                    array(
                        'class'=>'CFileLogRoute',
                        'levels'=>'trace, info',
                        'categories'=>'system.*',
                    ),
                    array(
                        'class'=>'CEmailLogRoute',
                        'levels'=>'error, warning',
                        'emails'=>'admin@example.com',
                    ),
                ),
            ),
        ),
    )

注册使用名为log的组件，组件对应的类为CLogRouter（见类文件yii/framework/logging/CLogRouter.php），并且需要为组件提供参数routes，
从目录yii/framework/logging可以看到可使用的日志输出目标路由有：`CDbLogRoute`（将日志记录到数据库中）、`CEmailLogRoute`（将日志发送到邮箱）、`CFileLogRoute`（记录到文件中）、`CWebLogRoute`（将日志显示在对应的网页中）、`CProfileLogRoute`，其中CProfileLogRoute直接继承自CWebLogRoute，其他路由类都直接继承自CLogRoute类。

至于为什么需要对log组件进行preload，即预先实例化，后边再说。

### 分析

先来看看Yii::log和Yii::trace的实现：

    :::php
    /**
     * Writes a trace message.
     * This method will only log a message when the application is in debug mode.
     * @param string $msg message to be logged
     * @param string $category category of the message
     * @see log
     */
    public static function trace($msg,$category='application')
    {
        // 得先定义常量YII_DEBUG为true
        if(YII_DEBUG)
            // CLogger::LEVEL_TRACE
            self::log($msg,CLogger::LEVEL_TRACE,$category);
    }

    /**
     * Logs a message.
     * Messages logged by this method may be retrieved via {@link CLogger::getLogs}
     * and may be recorded in different media, such as file, email, database, using
     * {@link CLogRouter}.
     * @param string $msg message to be logged
     * @param string $level level of the message (e.g. 'trace', 'warning', 'error'). It is case-insensitive.
     * @param string $category category of the message (e.g. 'system.web'). It is case-insensitive.
     */
    public static function log($msg,$level=CLogger::LEVEL_INFO,$category='application')
    {
        if(self::$_logger===null)
            self::$_logger=new CLogger;
        // 注意这里的常量YII_TRACE_LEVEL，如果想日志中含有对应文件名、对应行，那么应该定义YII_TRACE_LEVEL大于0，
        // 这个常量的意思应该是日志追踪的深度
        if(YII_DEBUG && YII_TRACE_LEVEL>0 && $level!==CLogger::LEVEL_PROFILE)
        {
            $traces=debug_backtrace();
            $count=0;
            foreach($traces as $trace)
            {
                if(isset($trace['file'],$trace['line']) && strpos($trace['file'],YII_PATH)!==0)
                {
                    $msg.="\nin ".$trace['file'].' ('.$trace['line'].')';
                    if(++$count>=YII_TRACE_LEVEL)
                        break;
                }
            }
        }
        // 调用的是CLogger类的log方法
        self::$_logger->log($msg,$level,$category);
    }

CLogger类的log方法实现如下所示：

    :::php
    /**
     * Logs a message.
     * Messages logged by this method may be retrieved back via {@link getLogs}.
     * @param string $message message to be logged
     * @param string $level level of the message (e.g. 'Trace', 'Warning', 'Error'). It is case-insensitive.
     * @param string $category category of the message (e.g. 'system.web'). It is case-insensitive.
     * @see getLogs
     */
    public function log($message,$level='info',$category='application')
    {
        $this->_logs[]=array($message,$level,$category,microtime(true));
        $this->_logCount++;
        // autoFlush的默认值为10000，即只有当日志的条数达到10000（或请求处理结束时），才会flush到输出，否则一直将日志存放在内存中
        if($this->autoFlush>0 && $this->_logCount>=$this->autoFlush && !$this->_processing)
        {
            $this->_processing=true;
            // autoDump默认为false
            $this->flush($this->autoDump);
            $this->_processing=false;
        }
    }

CLogger类的flush方法实现如下所示：

    :::php
    /**
     * Removes all recorded messages from the memory.
     * This method will raise an {@link onFlush} event.
     * The attached event handlers can process the log messages before they are removed.
     * @param boolean $dumpLogs whether to process the logs immediately as they are passed to log route
     * @since 1.1.0
     */
    public function flush($dumpLogs=false)
    {
        // 事件对象中会带有当前的CLogger对象，作为事件的发送者
        // 但在类CLogRouter的方法collectLogs和processLogs中并没有使用这个CLogger对象，
        // 而是通过Yii::getLogger()来得到同一个CLogger对象，为什么不直接使用呢？
        $this->onFlush(new CEvent($this, array('dumpLogs'=>$dumpLogs)));
        // 清空重置
        $this->_logs=array();
        $this->_logCount=0;
    }

    /**
     * Raises an <code>onFlush</code> event.
     * @param CEvent $event the event parameter
     * @since 1.1.0
     */
    public function onFlush($event)
    {
        // 抛出onFlush事件
        // raiseEvent方法定义在CComponent类中，CLogger类继承自CComponent类
        $this->raiseEvent('onFlush', $event);
    }

CComponent类的raiseEvent方法实现如下所示：

    :::php
    /**
     * Raises an event.
     * This method represents the happening of an event. It invokes
     * all attached handlers for the event.
     * @param string $name the event name
     * @param CEvent $event the event parameter
     * @throws CException if the event is undefined or an event handler is invalid.
     */
    public function raiseEvent($name,$event)
    {
        $name=strtolower($name);
        if(isset($this->_e[$name]))
        {
            // 逐个执行与事件$name绑定的$handler
            foreach($this->_e[$name] as $handler)
            {
                if(is_string($handler))
                    // 会将事件对象(CEvent对象)传到$handler中
                    call_user_func($handler,$event);
                elseif(is_callable($handler,true))
                {
                    if(is_array($handler))
                    {
                        // an array: 0 - object, 1 - method name
                        list($object,$method)=$handler;
                        if(is_string($object))  // static method call
                            call_user_func($handler,$event);
                        elseif(method_exists($object,$method))
                            $object->$method($event);
                        else
                            throw new CException(Yii::t('yii','Event "{class}.{event}" is attached with an invalid handler "{handler}".',
                                array('{class}'=>get_class($this), '{event}'=>$name, '{handler}'=>$handler[1])));
                    }
                    else // PHP 5.3: anonymous function
                        call_user_func($handler,$event);
                }
                else
                    throw new CException(Yii::t('yii','Event "{class}.{event}" is attached with an invalid handler "{handler}".',
                        array('{class}'=>get_class($this), '{event}'=>$name, '{handler}'=>gettype($handler))));
                // stop further handling if param.handled is set true
                if(($event instanceof CEvent) && $event->handled)
                    return;
            }
        }
        elseif(YII_DEBUG && !$this->hasEvent($name))
            throw new CException(Yii::t('yii','Event "{class}.{event}" is not defined.',
                array('{class}'=>get_class($this), '{event}'=>$name)));
    }

看到这里，你可能会很奇怪怎么都没看到真正记录日志的代码呢？在与事件绑定的各个$handler里呢，这也是log组件的routes参数配置成数组的原因，$handle就是该数组中对应类的实例化对象的日志记录方法。

那么这些$handle是在哪里绑定事件的呢？

既然log组件对应的是CLogRouter类，那么来看看其实现。

类CLogRouter继承自类CApplicationComponent。根据[Yii源码阅读笔记 - 组件集成](http://youngsterxyf.github.io/2014/11/13/read-yii-code-3/)一文，可知组件初始化时实例化对象会调用init方法来完成一些初始化操作，类CLogRouter的init方法实现如下所示：

    :::php
    /**
     * Initializes this application component.
     * This method is required by the IApplicationComponent interface.
     */
    public function init()
    {
        parent::init();
        // 实例化配置的routes参数中指定的日志路由类列表
        foreach($this->_routes as $name=>$route)
        {
            $route=Yii::createComponent($route);
            $route->init();
            $this->_routes[$name]=$route;
        }
        // 将当前对象的collectLogs方法绑定到事件onFlush
        Yii::getLogger()->attachEventHandler('onFlush',array($this,'collectLogs'));
        // 将当前对象的processLogs方法绑定到事件onEndRequest（表示请求处理结束？）
        Yii::app()->attachEventHandler('onEndRequest',array($this,'processLogs'));
    }

而类CLogRouter的方法collectLogs和processLogs实现如下所示：

    :::php
    /**
     * Collects log messages from a logger.
     * This method is an event handler to the {@link CLogger::onFlush} event.
     * @param CEvent $event event parameter
     */
    public function collectLogs($event)
    {
        $logger=Yii::getLogger();
        $dumpLogs=isset($event->params['dumpLogs']) && $event->params['dumpLogs'];
        // 遍历所有日志路由对象，执行其方法collectLogs
        foreach($this->_routes as $route)
        {
            // 属性enabled默认值为true
            if($route->enabled)
                // $dumpLogs默认为false，由事件对象传过来
                $route->collectLogs($logger,$dumpLogs);
        }
    }

    /**
     * Collects and processes log messages from a logger.
     * This method is an event handler to the {@link CApplication::onEndRequest} event.
     * @param CEvent $event event parameter
     * @since 1.1.0
     */
    public function processLogs($event)
    {
        $logger=Yii::getLogger();
        // 遍历所有日志路由对象，执行其方法collectLogs
        foreach($this->_routes as $route)
        {
            if($route->enabled)
                // 注意这里参数$dumpLogs参数值始终为true
                $route->collectLogs($logger,true);
        }
    }

以类CWebLogRoute为例来看看日志路由类的方法collectLogs，该方法定义于类CLogRoute中，实现如下所示：

    :::php
    /**
     * Retrieves filtered log messages from logger for further processing.
     * @param CLogger $logger logger instance
     * @param boolean $processLogs whether to process the logs after they are collected from the logger
     */
    // 事件onFlush触发时，传入的$processLogs参数值默认为false，事件onEndRequest触发时为true
    public function collectLogs($logger, $processLogs=false)
    {
        // 从类CLogger实例化对象的_logs属性值中过滤得到目标日志记录
        $logs=$logger->getLogs($this->levels,$this->categories,$this->except);
        $this->logs=empty($this->logs) ? $logs : array_merge($this->logs,$logs);
        if($processLogs && !empty($this->logs))
        {
            if($this->filter!==null)
                Yii::createComponent($this->filter)->filter($this->logs);
            if($this->logs!==array())
                // 调用实际route的processLogs方法
                $this->processLogs($this->logs);
            $this->logs=array();
        }
    }

而类CWebLogRoute的processLogs方法实现如下所示：

    :::php
    /**
     * Displays the log messages.
     * @param array $logs list of log messages
     */
    public function processLogs($logs)
    {
        $this->render('log',$logs);
    }

    /**
     * Renders the view.
     * @param string $view the view name (file name without extension). The file is assumed to be located under framework/data/views.
     * @param array $data data to be passed to the view
     */
    protected function render($view,$data)
    {
        $app=Yii::app();
        $isAjax=$app->getRequest()->getIsAjaxRequest();
        $isFlash=$app->getRequest()->getIsFlashRequest();

        // 用firebug来显示日志信息的话？
        if($this->showInFireBug)
        {
            // do not output anything for ajax and/or flash requests if needed
            if($isAjax && $this->ignoreAjaxInFireBug || $isFlash && $this->ignoreFlashInFireBug)
                return;
            $view.='-firebug';
            if(($userAgent=$app->getRequest()->getUserAgent())!==null && preg_match('/msie [5-9]/i',$userAgent))
            {
                echo '<script type="text/javascript">';
                echo file_get_contents(dirname(__FILE__).'/../vendors/console-normalizer/normalizeconsole.min.js');
                echo "</script>\n";
            }
        }
        elseif(!($app instanceof CWebApplication) || $isAjax || $isFlash)
            return;

        // 渲染yii/framework/views/log.php（log-firebug.php），将结果放在实际请求页面内容的下面
        $viewFile=YII_PATH.DIRECTORY_SEPARATOR.'views'.DIRECTORY_SEPARATOR.$view.'.php';
        include($app->findLocalizedFile($viewFile,'en'));
    }

从上述代码可以知道日志路由类是将日志信息按照一定格式显示在实际请求页面内容的下方。

再来看看方法init中调用的两个attachEventHandler，它们的定义是同一个，定义在类CComponent中（类CLogger直接继承自类CComponent），实现如下所示：

    :::php
    public function attachEventHandler($name,$handler)
    {
        // 将事件处理器$handler加到处理器列表中，在事件发生时会逐个处理器触发执行
        $this->getEventHandlers($name)->add($handler);
    }

其中方法EventHandlers的实现如下所示：

    :::php
    /**
     * Returns the list of attached event handlers for an event.
     * @param string $name the event name
     * @return CList list of attached event handlers for the event
     * @throws CException if the event is not defined
     */
    public function getEventHandlers($name)
    {
        if($this->hasEvent($name))
        {
            $name=strtolower($name);
            if(!isset($this->_e[$name]))
                $this->_e[$name]=new CList;
            return $this->_e[$name];
        }
        else
            throw new CException(Yii::t('yii','Event "{class}.{event}" is not defined.',
                array('{class}'=>get_class($this), '{event}'=>$name)));
    }

从上述分析可以知道所谓事件系统，其实就是将处理函数/对象方法放到与事件ID对应的一个列表中，然后在事件触发时，逐个调用执行这些函数/对象方法。

Yii框架基于事件系统，可以做到同时将日志信息写到多个目标输出中。

------

回到之前提到的那个问题：为什么需要对log组件进行preload？

这是因为：对于日志组件的使用并不是通过`Yii::app()->db`这种形式来调用的（如果基于这种形式，那么就可以在首次调用时再做组件实例化，以实现组件延迟加载），而是通过触发事件来间接调用，但这就需要在事件触发之间将相关的处理函数/对象方法绑定到事件，这个绑定操作又是在日志log组件的init方法中执行的，一般组件类实例化时才会调用其init方法，所以需要对log组件进行预加载。

### 参考

- [Yii - topics - Logging](http://www.yiiframework.com/doc/guide/1.1/en/topics.logging)
