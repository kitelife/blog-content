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

类CWebApplication自己也没有实现构造方法，直接继承自抽象类CApplication，其构造方法实现如下：

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

构造方法根据配置信息初始化一些路径