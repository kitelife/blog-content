Title: Yii源码阅读笔记 - 请求处理基本流程
Date: 2014-11-04
Author: youngsterxyf
Slug: read-yii-code-1
Tags: PHP, Yii, 笔记, 总结

对于Web框架，我认为其主要有三点作用：

1. 提供多人协作的基本规范
2. 避免重复造轮子
3. 开发者只需关注业务逻辑，脏活（如：基本的安全防范、兼容问题）Web框架都已完成并提供设计良好的API

但代价是学习成本 - 为了尽可能发挥Web框架的优势，需要花一些阅读文档，甚至是框架源码（特别是文档缺乏或者文档写得垃圾的），然后经过几次项目实践，一切才能了然于胸。

喏，为了在工作中更好地使用、避免误用Yii框架，大致阅读了Yii框架的部分代码，然后有了这个系列的笔记。

------

深入学习一个Web框架，首先要理解的是请求处理流程。对于PHP而言，处理流程也即包含了应用的初始化过程，如加载配置、初始化组件等。请求处理流程中最核心的应该是路由解析和分发，此外可能还有过滤器处理、事件处理等，直到请求处理进入具体的Controller和Action。响应生成、过滤等也可以关注。

------

基于Yii框架的工程目录结构大致如下所示：

![Yii-Project-Structure](/assets/uploads/pics/yii-project-structure.png)

- index.php是应用的入口
- protected目录是存放动态脚本的地方
	- components子目录存放各种组件类
	- configs存放应用的配置文件
	- controllers存放Controller类文件
	- models存放Model类文件
	- runtime存放一些应用生成的临时文件或者缓存文件，如Smarty编译好的模板、日志文件
	- views存放View模板文件
- static目录存放静态文件，如CSS、JS、图片等
- yii目录则存放Yii框架的源码

`index.php`文件的内容大致如下：

	:::php
    <?php
    defined('APP_ENV') or define('APP_ENV', 'development');
	if (APP_ENV == 'production') {
    	ini_set('display_errors', 0);
    	error_reporting(E_ALL);
    	define('YII_ENABLE_ERROR_HANDLER', false);
    	$yii = dirname(__FILE__) . '/yii/framework/yiilite.php';
    	defined('YII_TRACE_LEVEL') or define('YII_TRACE_LEVEL', 1);
	} else {
    	error_reporting(E_ALL);
    	$yii = dirname(__FILE__) . '/yii/framework/yii.php';
    	defined('YII_DEBUG') or define('YII_DEBUG', true);
    	defined('YII_TRACE_LEVEL') or define('YII_TRACE_LEVEL', 3);
	}
	$config = dirname(__FILE__) . '/protected/configs/' . APP_ENV . '.php';

	require_once($yii);
	$YiiApp = Yii::createWebApplication($config);
	$YiiApp->run();

根据应用所处的环境（开发环境或生产环境）配置不同的环境变量，加载不同的配置文件，然后根据配置信息创建一个Web应用对象（这个对象类似一个容器），并处理请求。

`Yii::createWebApplication($config)`中类Yii直接继承自类YiiBase，并且没有自定义属性和方法，即调用的静态方法createWebApplication来自类YiiBase，实现如下：

	:::php
    public static function createWebApplication($config=null)
    {
    	return self::createApplication('CWebApplication', $config);
    }

之所以这么实现，是因为Yii还支持控制台/命令行类型的应用实现，比如cron脚本。

静态方法createApplication实现如下：

	:::php
    public static function createApplication($class, $config=null)
    {
    	return new $class($config);
    }

真正实例化的类CWebApplication见文件`yii/framework/web/CWebApplication.php`。

类CWebApplication自己也没有实现构造方法，直接继承自抽象类CApplication（见文件`yii/framework/base/CApplication.php`），其构造方法实现如下：

	:::php
    public function __construct($config=null)
	{
		Yii::setApplication($this);

		// set basePath at early as possible to avoid trouble
		if(is_string($config))
			$config=require($config);
		if(isset($config['basePath']))
		{
			$this->setBasePath($config['basePath']);
			unset($config['basePath']);
		}
		else
			$this->setBasePath('protected');
		Yii::setPathOfAlias('application',$this->getBasePath());
		Yii::setPathOfAlias('webroot',dirname($_SERVER['SCRIPT_FILENAME']));
		if(isset($config['extensionPath']))
		{
			$this->setExtensionPath($config['extensionPath']);
			unset($config['extensionPath']);
		}
		else
			Yii::setPathOfAlias('ext',$this->getBasePath().DIRECTORY_SEPARATOR.'extensions');
		if(isset($config['aliases']))
		{
			$this->setAliases($config['aliases']);
			unset($config['aliases']);
		}

		$this->preinit();

		$this->initSystemHandlers();
		$this->registerCoreComponents();

		$this->configure($config);
		$this->attachBehaviors($this->behaviors);
		$this->preloadComponents();

		$this->init();
	}

`Yii::setApplication($this)`将当前类CWebApplication的实例化对象赋值给类YiiBase的私有属性`$_app`，之后通过`Yii::app()`就能取到这个对象（app方法其实是类YiiBase中定义的）。

构造方法根据配置信息初始化一些路径和别名相关的属性。以路径别名`application`为例，如果想将日志目录配置为`protected/runtime`，则可以指定路径为`application.runtime`，这样的好处是你可以配置`basePath`来指定动态脚本所在的目录，不一定必须是`protected`，即使你的修改了basePath，其余相对basePath的路径配置都不需要变动。

类CApplication又直接继承自类CModule（见文件`yii/framework/base/CModule.php`），上述构造方法中调用的方法`preinit`、`configure`、`preloadComponents`定义在类CModule中。

`preinit`的方法体为空。这个方法调用之后主要是加载核心组件、及将配置信息存到`Yii::app()`这个容器对象中。如果需要在这些操作之前做一些初始化准备工作，则可以自定义一个类继承自类`CWebApplication`，然后实现`preinit`方法。但这样的话，index.php中创建web应用对象的方式就有所不同的了，假设自定义的类为`MyWebApplication`，index.php中在引入该类文件后：

	:::php
    $yiiApp = Yii::createApplication('MyWebApplication', $config);
    $yiiApp->run();

方法`initSystemHandler`则是根据条件设置框架的异常和错误处理方法。

方法`registerCoreComponents`则是加载框架的核心组件，当然如果有需要可以配置同名（同名指的是key相同，Yii中每个组件都是通过一个key或者说别名来注册和引用）的自定义组件来覆盖默认的核心组件，如db、urlManager。

组件的注册加载细节我们会另外写一篇文章来介绍。

------

方法`configure`定义在类`CModule`中，实现如下：

	:::php
    public function configure($config)
	{
		if(is_array($config))
		{
			foreach($config as $key=>$value)
				$this->$key=$value;
		}
	}

看起来是不是很简单？但其实没你想的那么简单呢... 思考一下如果代码中当前对象`$this`不存在属性`$key`或者名为`$key`的属性是私有的会发生什么事情？这时PHP的魔术方法`__set`就派上用场了。

类`CModule`直接继承自类`CComponent`。在类CComponent中定义了方法`__set`，实现如下：

	:::php
    public function __set($name,$value)
	{
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

PHP中对一个对象的属性进行赋值的规则如下：

1. 如果该对象有public的该属性，则直接赋值
2. 否则看该对象所在继承树上是否有定义魔术方法`__set`，如果有则调用`__set`来处理赋值过程
3. 如果连`__set`也没有，则为该对象生成一个public的属性，然后赋值给它

类CComponent中定义的魔术方法`__set`其逻辑是：

1. 查看当前对象是否有名为`'set'.$key`的方法，如果有，则以该方法来处理赋值过程
2. 否则，检查$key是否以字符串`on`开头，如果是且当前对象具有名为$key的方法，则认为这是一个事件的赋值过程，将赋值到事件列表中
3. 否则，则认为这是一个行为(behavior)赋值，尝试为属性`_m`对象列表中对象的属性赋值。（貌似是这样，我也还懂`_m`的作用）

以上述规则逻辑，所以类CModule中定义了很多方法名以字符串`set`或`get`开头的方法，如setComponents、getComponents、setParams、getParams等。说到这里，你是不是领会到什么了？

------

`$this->attachBehaviors($this->behaviors)`一句中当前对象的属性behaviors的访问权限为public，默认值为空数组，可以在配置文件中配置如下一项：

	:::php
    'behaviors' => array(
    	'behaviorName'=>array(
    		'class'=>'path.to.BehaviorClass',
    		'property1'=>'value1',
    		'property2'=>'value2',
		)
    ),

按照上述对象属性的赋值规则，该配置项会赋值给属性behaviors。

方法attachBehaviors对这些配置项逐个初始化然后存入属性`_m`中。

------

方法`preloadComponents`定义在类CModule中，实现如下：

	:::php
    /**
	 * Loads static application components.
	 */
	protected function preloadComponents()
	{
		foreach($this->preload as $id)
			$this->getComponent($id);
	}

其中属性preload访问权限为public，默认也是空数组，可以在其中配置需要预加载的组件的ID。

------

`$this->init()`一行中方法`init`定义在类CWebApplication中，实现如下：

	:::php
    protected function init()
	{
		parent::init();
		// preload 'request' so that it has chance to respond to onBeginRequest event.
		$this->getRequest();
	}

其中方法`getRequest`就是预加载request组件。

------

index.php中得到Web应用对象后继而调用其方法run，该run方法定义于类CApplication中，实现如下：

	:::php
    /**
	 * Runs the application.
	 * This method loads static application components. Derived classes usually overrides this
	 * method to do more application-specific tasks.
	 * Remember to call the parent implementation so that static application components are loaded.
	 */
	public function run()
	{
		if($this->hasEventHandler('onBeginRequest'))
			$this->onBeginRequest(new CEvent($this));
        // 这里为了处理程序主动调用exit()或者抛出异常时的情况
		register_shutdown_function(array($this,'end'),0,false);
        // 请求处理
		$this->processRequest();
		if($this->hasEventHandler('onEndRequest'))
			$this->onEndRequest(new CEvent($this));
	}

其中方法processRequest定义于类CWebApplication中，实现如下：

	:::php
    public function processRequest()
	{
    	// 可以在配置文件里配置request组件时，提供catchAllRequest参数
    	// catchAllRequest是一个数组，第一个元素指定一个controller及一个action，其余元素是这个action的参数
    	// 如果配置了catchAllRequest，就可以用这个controller/action来处理所有的请求，当网站进入维护状态时，有其用处。
    	if(is_array($this->catchAllRequest) && isset($this->catchAllRequest[0]))
    	{
        	$route=$this->catchAllRequest[0];
        	foreach(array_splice($this->catchAllRequest,1) as $name=>$value)
            	$_GET[$name]=$value;
    	}
    	else
        	// 正常的路由解析
        	// 组件urlManager ->parseUrl 组件request
        	$route=$this->getUrlManager()->parseUrl($this->getRequest());
    	// 根据路由执行控制器处理函数
    	$this->runController($route);
	}

其中路由解析的过程我们也会以单独的一篇文章来分析，暂不细说。

方法runController的实现如下：

	:::php
    /**
	 * Creates the controller and performs the specified action.
	 * @param string $route the route of the current request. See {@link createController} for more details.
	 * @throws CHttpException if the controller could not be created.
	 */
	public function runController($route)
	{
		if(($ca=$this->createController($route))!==null)
		{
			list($controller,$actionID)=$ca;
			$oldController=$this->_controller;
			$this->_controller=$controller;
			$controller->init();
			$controller->run($actionID);
			$this->_controller=$oldController;
		}
		else
			throw new CHttpException(404,Yii::t('yii','Unable to resolve the request "{route}".',
				array('{route}'=>$route===''?$this->defaultController:$route)));
	}

其中方法Controller根据$route按照一定的规则找到对应的controller类，之后调用controller的init方法和run方法。但这个调用之前和之后还恢复老的controller，这应该是因为在一个controller中可以forward到另一个controller中去，也即controller可以递归执行，所以需要保存和恢复上下文。

Yii中所有Controller类都必须直接或间接继承自类CController，该类的init方法实现为空，如有需要可以在子类中重写。而其run方法实现如下：

	:::php
    public function run($actionID)
	{
		if(($action=$this->createAction($actionID))!==null)
		{
			if(($parent=$this->getModule())===null)
				$parent=Yii::app();
			if($parent->beforeControllerAction($this,$action))
			{
				$this->runActionWithFilters($action,$this->filters());
				$parent->afterControllerAction($this,$action);
			}
		}
		else
			$this->missingAction($actionID);
	}

`$this->runActionWithFilters($action,$this->filters())`一行中，方法filters的实现仅是返回一个空数组，如果想要使用过滤器就需要在自定义的Controller类中重写该方法，过滤器的配置方法见源码中注释：

	:::text
    * For a method-based filter (called inline filter), it is specified as 'FilterName[ +|- Action1, Action2, ...]',
	 * where the '+' ('-') operators describe which actions should be (should not be) applied with the filter.
	 *
	 * For a class-based filter, it is specified as an array like the following:
	 * <pre>
	 * array(
	 *     'FilterClass[ +|- Action1, Action2, ...]',
	 *     'name1'=>'value1',
	 *     'name2'=>'value2',
	 *     ...
	 * )
	 * </pre>
	 * where the name-value pairs will be used to initialize the properties of the filter.

方法runActionWithFilters实现如下：

	:::php
    public function runActionWithFilters($action,$filters)
	{
		if(empty($filters))
			$this->runAction($action);
		else
		{
			$priorAction=$this->_action;
			$this->_action=$action;
			CFilterChain::create($this,$action,$filters)->run();
			$this->_action=$priorAction;
		}
	}

如果没有设置过滤器，则直接执行目标action，方法runAction的实现如下：

	:::php
    public function runAction($action)
	{
    	$priorAction=$this->_action;
    	$this->_action=$action;
    	if($this->beforeAction($action))
    	{
        	if($action->runWithParams($this->getActionParams())===false)
            	$this->invalidActionParams($action);
        	else
            	$this->afterAction($action);
    	}
    	$this->_action=$priorAction;
	}

类CController中定义的beforeAction直接返回true，如果需要在目标action执行之前做一些检查过滤操作则需要在自定义的Controller类中重写beforeAction方法，该方法最后必须返回true或false。beforeAction的作用类似于简化版的过滤器。

beforeAction通过后，则执行目标action。由于路由配置是类正则的，URL解析出来的一些片段值（算是放在url中的请求参数）应该传入目标action，方法getActionParams即是取到这些参数值。Yii在路由解析时将这些参数值也存放到全局变量`$_GET`中，所以getActionParams直接返回了`$_GET`。

------

如果设置了过滤器，则需要根据controller、action、filters创建一个CFilterChain对象（过程中当然会对过滤器配置进行解析），类CFilterChain的run方法实现如下：

	:::php
    public function run()
	{
		if($this->offsetExists($this->filterIndex))
		{
			$filter=$this->itemAt($this->filterIndex++);
			Yii::trace('Running filter '.($filter instanceof CInlineFilter ? get_class($this->controller).'.filter'.$filter->name.'()':get_class($filter).'.filter()'),'system.web.filters.CFilterChain');
			$filter->filter($this);
		}
		else
			$this->controller->runAction($this->action);
	}

其中`$this->filterIndex`的初始值为0，方法offsetExits定义于类CList中，逻辑就是检测是否遍历执行完所有的过滤器，如果还有，则取出一个过滤器对象，执行其filter方法，该方法的实现如下：

	:::php
    public function filter($filterChain)
	{
		$method='filter'.$this->name;
		$filterChain->controller->$method($filterChain);
	}

这个时候你应该感到疑惑 - 既然是一个过滤器链，那么循环在哪？事实上，Yii的这个地方并没有提供循环来让过滤器逐个执行，这就意味着在自定义的过滤器中，如果过滤条件通过，则需要尾递归地显式调用过滤器链的run方法，这样直到所有的过滤器都通过，才执行目标action`$this->controller->runAction($this->action)`。