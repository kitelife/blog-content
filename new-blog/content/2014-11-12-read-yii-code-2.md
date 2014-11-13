Title: Yii源码阅读笔记 - 路由解析
Date: 2014-11-12
Author: youngsterxyf
Slug: read-yii-code-2
Tags: PHP, Yii, 笔记, 总结


### 概述

Yii框架的路由解析功能由核心组件urlManager来完成。路由的形式有两种：

- get：通过URL中查询字符串（query string）参数r来指定路由，如：`r=controllerID/actionID`
- path：直接通过URL来指定，如：`/controllerID/actionID`

默认使用get路由形式。由于Yii中controller类命名和action方法都是按照规则命名的，而路由也是按照规则来匹配的，所以完全可以不用额外配置urlManager。

若需要使用path方式，则可如下配置：

    :::php
    "components" => array(
        'urlManager' => array(
            'urlFormat' => 'path',
            'rules' => array(
                ...
            ),
    ),

进一步说明可参考[RESTful API设计的一点经验](http://youngsterxyf.github.io/2014/09/06/experience-about-restful-api/)一文。

### 分析

在“请求处理基本流程”一篇可以看到Yii框架路由解析流程的入口在类CWebApplication的processRequest方法中：

	:::php
    $route=$this->getUrlManager()->parseUrl($this->getRequest());

其中getUrlManager方法定义于类CApplication中，作用是初始化获取URL管理组件（ID为urlManager），实现如下：

	:::php
    public function getUrlManager()
	{
		return $this->getComponent('urlManager');
	}
    
在获取urlManager组件对象过程中，会对对象做初始化，调用对象的init方法，见类CUrlManager的init方法实现：

    :::php
    public function init()
	{
		parent::init();
		$this->processRules();
	}
    
其中调用的方法processRules，是根据配置的rules解析创建规则对象，放到属性_rules中，实现如下：

    :::php
    protected function processRules()
	{
        // 如果未配置rules，或使用的路由形式是get，则根本无需解析路由规则
		if(empty($this->rules) || $this->getUrlFormat()===self::GET_FORMAT)
			return;
        // 否则尝试从缓存中读取解析好的路由规则
		if($this->cacheID!==false && ($cache=Yii::app()->getComponent($this->cacheID))!==null)
		{
			$hash=md5(serialize($this->rules));
			if(($data=$cache->get(self::CACHE_KEY))!==false && isset($data[1]) && $data[1]===$hash)
			{
				$this->_rules=$data[0];
				return;
			}
		}
        // 否则逐条路由规则解析
		foreach($this->rules as $pattern=>$route)
			$this->_rules[]=$this->createUrlRule($route,$pattern);
        // 尝试缓存解析好的路由规则
		if(isset($cache))
			$cache->set(self::CACHE_KEY,array($this->_rules,$hash));
	}
    
从上述代码中，在解析创建规则对象前会先检查是否已缓存了解析创建好的规则，如果没有，则在解析创建好规则后，将这些规则缓存起来。这样就避免了每次请求处理都要解析一次rules列表。
但这里需要注意的是**urlManager组件默认使用ID为`cache`的缓存组件（CUrlManager类的属性cacheID默认值为cache），而核心组件并不包含ID为`cache`的缓存组件，所以若希望缓存解析好路由规则，
则应该配置ID为cache的缓存组件，如果缓存组件的ID不是cache，则需要配置urlManager组件的cacheID属性**。

如果没有设置缓存组件，或者缓存中未找到解析好的路由规则，则需要对配置的rules逐条解析，解析过程见类CUrlManager的createUrlRule方法实现：

    :::php
    /**
	 * Creates a URL rule instance.
	 * The default implementation returns a CUrlRule object.
	 * @param mixed $route the route part of the rule. This could be a string or an array
	 * @param string $pattern the pattern part of the rule
	 * @return CUrlRule the URL rule instance
	 * @since 1.1.0
	 */
	protected function createUrlRule($route,$pattern)
	{
        // 说明可以配置自定义的路由规则解析类
		if(is_array($route) && isset($route['class']))
			return $route;
		else
		{
			$urlRuleClass=Yii::import($this->urlRuleClass,true);
			return new $urlRuleClass($route,$pattern);
		}
	}
    
以以下rules配置为例：

    :::php
    'rules' => array(
        array('industry/index', 'pattern' => '/v1/partner/industry/', 'verb' => 'GET'),
        array('token/create', 'pattern' => '/v1/partner/token', 'verb' => 'POST'),
    )

在处理第一条规则时，方法createUrlRule的参数$pattern的值为数组的索引0，$route的值为关联数组`array('industry/index', 'pattern' => '/v1/partner/industry/', 'verb' => 'GET')`，
但因为$route里没有设置class字段，所以走的是else分支 - 先引入类CUrlRule（$this->urlRuleClass的默认值），然后根据$route、$pattern实例化类CUrlRule，该类也定义在文件`yii/framework/web/CUrlManager.php`中，
直接继承自抽象类CBaseUrlRule。CUrlRule的构造方法实现如下：

    :::php
    public function __construct($route,$pattern)
	{
		if(is_array($route))
		{
            // 从这里可知$route支持'urlSuffix', 'caseSensitive', 'defaultParams', 'matchValue', 'verb', 'parsingOnly'这些配置项
			foreach(array('urlSuffix', 'caseSensitive', 'defaultParams', 'matchValue', 'verb', 'parsingOnly') as $name)
			{
				if(isset($route[$name]))
					$this->$name=$route[$name];
			}
            // 如果$route中有pattern配置项，则将配置值赋值给$pattern
			if(isset($route['pattern']))
				$pattern=$route['pattern'];
            // 而$route的第一个配置项才是真正的目标路由
			$route=$route[0];
		}
		$this->route=trim($route,'/');

		$tr2['/']=$tr['/']='\\/';

		if(strpos($route,'<')!==false && preg_match_all('/<(\w+)>/',$route,$matches2))
		{
			foreach($matches2[1] as $name)
				$this->references[$name]="<$name>";
		}

        // 是否带协议头
		$this->hasHostInfo=!strncasecmp($pattern,'http://',7) || !strncasecmp($pattern,'https://',8);

        // 如果原$route有verb配置项
        // verb配置支持多个HTTP方法，以空格或逗号分隔，如：“GET,POST”
		if($this->verb!==null)
			$this->verb=preg_split('/[\s,]+/',strtoupper($this->verb),-1,PREG_SPLIT_NO_EMPTY);

        // $pattern中类正则片段支持两种形式：命名的和未命名的，如“<id:\d+>”和“<\d+>”
		if(preg_match_all('/<(\w+):?(.*?)?>/',$pattern,$matches))
		{
			$tokens=array_combine($matches[1],$matches[2]);
			foreach($tokens as $name=>$value)
			{
				if($value==='')
					$value='[^\/]+';
				$tr["<$name>"]="(?P<$name>$value)";
				if(isset($this->references[$name]))
					$tr2["<$name>"]=$tr["<$name>"];
				else
					$this->params[$name]=$value;
			}
		}
        // 好吧，之后的这段代码我还没太看懂作用
        // 就是为了将$pattern转换成一个真正的正则表达式？
		$p=rtrim($pattern,'*');
		$this->append=$p!==$pattern;
		$p=trim($p,'/');
		$this->template=preg_replace('/<(\w+):?.*?>/','<$1>',$p);
		$this->pattern='/^'.strtr($this->template,$tr).'\/';
		if($this->append)
			$this->pattern.='/u';
		else
			$this->pattern.='$/u';

		if($this->references!==array())
			$this->routePattern='/^'.strtr($this->route,$tr2).'$/u';

		if(YII_DEBUG && @preg_match($this->pattern,'test')===false)
			throw new CException(Yii::t('yii','The URL pattern "{pattern}" for route "{route}" is not a valid regular expression.',
				array('{route}'=>$route,'{pattern}'=>$pattern)));
	}

------

在得到**urlManager组件对象**后，调用其parseUrl方法，实现如下：

    :::php
    public function parseUrl($request)
	{
		if($this->getUrlFormat()===self::PATH_FORMAT)
		{
			$rawPathInfo=$request->getPathInfo();
			$pathInfo=$this->removeUrlSuffix($rawPathInfo,$this->urlSuffix);
			foreach($this->_rules as $i=>$rule)
			{
				if(is_array($rule))
					$this->_rules[$i]=$rule=Yii::createComponent($rule);
                // 逐个路由规则匹配
				if(($r=$rule->parseUrl($this,$request,$pathInfo,$rawPathInfo))!==false)
                    // 即使匹配到了路由规则，也还是得看一下URL中是否指定了路由，是的话则优先使用URL中指定的路由
					return isset($_GET[$this->routeVar]) ? $_GET[$this->routeVar] : $r;
			}
            // 如果一定要匹配到某个路由规则才行，那么执行到这里就表示未有匹配的路由规则，所以就抛404错误了。
			if($this->useStrictParsing)
				throw new CHttpException(404,Yii::t('yii','Unable to resolve the request "{route}".',
					array('{route}'=>$pathInfo)));
            // 否则先返回请求路径作为目标路由
			else
				return $pathInfo;
		}
        // 如果使用的是get路由形式，则从GET请求的查询字符串或POST请求的请求体找目标路由
		elseif(isset($_GET[$this->routeVar]))
			return $_GET[$this->routeVar];
		elseif(isset($_POST[$this->routeVar]))
			return $_POST[$this->routeVar];
		else
			return '';
	}
    
方法的参数是一个request组件对象。

先判断应用使用的路由形式是否为path，如果不是，则根据路由的参数名（默认为`r`，由于urlManager类的routeVar属性是public的，所以可以通过配置routeVar的值来修改路由参数名）获取路由。并且路由可以通过GET方法放在URL查询字符串中，也可以通过POST方法放在请求体中。

对于path形式的路由，解析过程则要复杂一些。先通过request组件对象的getPathInfo方法取到请求的URL（会对原本的请求URL做一定的处理），然后根据解析好的路由规则列表逐个匹配。其中**CUrlRule类**的parseUrl方法实现如下：

    :::php
    public function parseUrl($manager,$request,$pathInfo,$rawPathInfo)
	{
        // 先检查HTTP谓词（verb）是否匹配
		if($this->verb!==null && !in_array($request->getRequestType(), $this->verb, true))
			return false;
        // 是否关心大小写
		if($manager->caseSensitive && $this->caseSensitive===null || $this->caseSensitive)
			$case='';
		else
			$case='i';

        // urlSiffix配置项是用来干嘛的？
		if($this->urlSuffix!==null)
			$pathInfo=$manager->removeUrlSuffix($rawPathInfo,$this->urlSuffix);

		// URL suffix required, but not found in the requested URL
		if($manager->useStrictParsing && $pathInfo===$rawPathInfo)
		{
			$urlSuffix=$this->urlSuffix===null ? $manager->urlSuffix : $this->urlSuffix;
			if($urlSuffix!='' && $urlSuffix!=='/')
				return false;
		}

		if($this->hasHostInfo)
			$pathInfo=strtolower($request->getHostInfo()).rtrim('/'.$pathInfo,'/');

		$pathInfo.='/';

        // 正则匹配：用pattern来匹配路径
		if(preg_match($this->pattern.$case,$pathInfo,$matches))
		{
            // 可以配置defaultParams数组来为请求未提供的必要参数指定默认值
			foreach($this->defaultParams as $name=>$value)
			{
				if(!isset($_GET[$name]))
					$_REQUEST[$name]=$_GET[$name]=$value;
			}
			$tr=array();
			foreach($matches as $key=>$value)
			{
				if(isset($this->references[$key]))
					$tr[$this->references[$key]]=$value;
				elseif(isset($this->params[$key]))
					$_REQUEST[$key]=$_GET[$key]=$value;
			}
			if($pathInfo!==$matches[0]) // there're additional GET params
				$manager->parsePathInfo(ltrim(substr($pathInfo,strlen($matches[0])),'/'));
			if($this->routePattern!==null)
				return strtr($this->route,$tr);
			else
				return $this->route;
		}
		else
			return false;
	}
    
从上述代码可以看出，路由解析关键是根据$pattern匹配请求URL，并**从URL取出需要的东西作为请求参数**，一旦匹配，就以$route作为该次请求的目标路由。

获得目标路由后，就可以根据目标路由查找调用对应的controller和action了。