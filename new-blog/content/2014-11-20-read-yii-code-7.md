Title: Yii源码阅读笔记 - 应用模块化
Date: 2014-11-20
Author: youngsterxyf
Slug: read-yii-code-7
Tags: PHP, Yii, 笔记, 总结


### 概述

Yii框架有个“模块（Module）”的概念，与“应用（Application）”类似，模块必须归属于一个父模块或者一个应用，模块不能单独部署，一个应用不一定要分模块。

由此可以看到，Yii的“模块”和“应用”类似于Django框架中的“应用（App）”和“项目（Project）”。

当一个应用的规模大到一定的程度 - 可能涉及多个团队来开发，就应该考虑分“模块”开发。“模块”通常对应应用的一个相对独立的功能。

一个模块化的Yii框架应用的工程目录结构大致示例如下：

![Yii-WebApp-Modules](/assets/uploads/pics/yii-webapp-modules.png)

上图所示项目有一个名为“forum”的模块，该模块下也有自己的`components`、`controllers`、`models`、`views`、`extensions`目录，与一个普通的/不分模块的Yii框架Web应用的项目结构非常相似。

Yii框架模块化应用的所有模块默认都是放在`protected/modules`目录下，每个模块的内容又各自放在以模块ID（如`forum`）为名称的子目录下，并且在模块子目录下要有一个模块类文件，如`ForumModule.php`，该类文件的命名规范是：模块ID首字母大写，然后拼接上字符串Module。

模块化的应用需要在配置文件中配置`modules`一项 - 指定模块列表，示例如下：

    :::php
    'modules' => array(
        'forum' => array(
            ...
        ),
        'anotherModule',
        ...
    ),

每个模块的配置，可以只指定模块ID，也可以通过数组来指定额外的信息，如模块类、类实例化参数、params、components，以及子模块等等。Yii中模块是可以嵌套的，并且嵌套深度没有限制（有这个必要么？不要玩脱了啊）。

对应某个模块中的控制器及控制器中的Action，路由中需要带模块ID前缀，如`moduleID/controllerID/actionID`，对于嵌套的模块，路由的形式则为`parentModuleID/childModuleID/controllerID/actionID`。路由分发逻辑会根据模块ID到配置信息中查找对应的模块，最终分发到某个模块的某个控制器的某个Action中做处理。

另外，Yii框架应用的模块化并不是必须把所有功能逻辑都拆分到各个模块，而是可以部分功能逻辑归到应用，部分逻辑归到模块，即可以不彻底地模块化，但个人认为最好别这么玩（应用下的controller的id和模块的id冲突怎么办？），并且最好不要用模块嵌套，以免搞得过于复杂，降低项目的可维护性。


### 分析

先从继承关系上看看“模块”与“应用”的相似性：

- `CWebApplication` -> `CApplication` -> `CModule` -> `CComponent`
- 自定义模块类 -> `CWebModule` -> `CModule` -> `CComponent`

由此可以看到继承链中类`CModule`及上溯类的属性和方法，“模块”类和“应用”都有。

------

由[Yii源码阅读笔记 - 请求处理基本流程](http://youngsterxyf.github.io/2014/11/04/read-yii-code-1/)一文可知，应用配置的加载是抽象类CApplication的构造方法中调用方法`configure`来完成的，
该方法定义于类`CModule`中，实现如下：

    :::php
    /**
     * Configures the module with the specified configuration.
     * @param array $config the configuration array
     */
    public function configure($config)
    {
        if(is_array($config))
        {
            foreach($config as $key=>$value)
                $this->$key=$value;
        }
    }

对于配置项“modules”的加载，则是通过类`CComponent`中的魔术方法`__set`最终调用类`CModule`中的`setModules`方法来完成的：

    :::php
    /**
     * Configures the sub-modules of this module.
     *
     * Call this method to declare sub-modules and configure them with their initial property values.
     * The parameter should be an array of module configurations. Each array element represents a single module,
     * which can be either a string representing the module ID or an ID-configuration pair representing
     * a module with the specified ID and the initial property values.
     *
     * For example, the following array declares two modules:
     * <pre>
     * array(
     *     'admin',                // a single module ID
     *     'payment'=>array(       // ID-configuration pair
     *         'server'=>'paymentserver.com',
     *     ),
     * )
     * </pre>
     *
     * By default, the module class is determined using the expression <code>ucfirst($moduleID).'Module'</code>.
     * And the class file is located under <code>modules/$moduleID</code>.
     * You may override this default by explicitly specifying the 'class' option in the configuration.
     *
     * You may also enable or disable a module by specifying the 'enabled' option in the configuration.
     *
     * @param array $modules module configurations.
     */
    public function setModules($modules)
    {
        foreach($modules as $id=>$module)
        {
            // 如果只指定了模块的id
            if(is_int($id))
            {
                $id=$module;
                $module=array();
            }
            // 如果未指定模块对应的模块类，则默认通过路径别名$id.'.'.ucfirst($id).'Module'来查找对应的模块类
            if(!isset($module['class']))
            {
                Yii::setPathOfAlias($id,$this->getModulePath().DIRECTORY_SEPARATOR.$id);
                $module['class']=$id.'.'.ucfirst($id).'Module';
            }

            // 将模块配置信息存入属性_moduleConfig中
            if(isset($this->_moduleConfig[$id]))
                $this->_moduleConfig[$id]=CMap::mergeArray($this->_moduleConfig[$id],$module);
            else
                $this->_moduleConfig[$id]=$module;
        }
    }

可以看到模块列表配置信息加载后并未对模块类进行实例化初始化。

------

请求处理在路由解析得到目标路由后，调用方法`createController`来做路由分发（这样表述可能不太严谨），该方法定义于类`CWebApplication`中，实现如下所示：

    :::php
    public function createController($route,$owner=null)
    {
        // 如果未提供参数$owner，即未指定当前$route所属的模块，则默认当前应用对象为owner，可以将应用当做是顶级模块
        if($owner===null)
            $owner=$this;
        // 如果路由为空，则使用默认路由
        // 应用的默认路由ID是site，模块的默认路由ID为default
        if(($route=trim($route,'/'))==='')
            $route=$owner->defaultController;
        // 路由是否大小写敏感
        $caseSensitive=$this->getUrlManager()->caseSensitive;

        $route.='/';
        // 如果路由中还有斜杠
        // 注意这里是个while循环
        while(($pos=strpos($route,'/'))!==false)
        {
            // 取出第一个斜杠之前的部分，用于之后的代码看看是否有对应该ID的controller或module
            $id=substr($route,0,$pos);
            if(!preg_match('/^\w+$/',$id))
                return null;
            if(!$caseSensitive)
                $id=strtolower($id);
            // 取出第一个斜杠之后的部分，用于可能的下一次循环处理
            $route=(string)substr($route,$pos+1);
            // 看看是否是第一次循环处理
            // $basePath是在第一次循环处理时在这个if条件分支中才赋值的，所以第一次循环处理到这里时$basePath是未定义
            if(!isset($basePath))  // first segment
            {
                // 先从应用或模块配置的controllerMap中看看是否有$id为key的controller，若有，则直接实例化对应的controll类并返回
                if(isset($owner->controllerMap[$id]))
                {
                    return array(
                        Yii::createComponent($owner->controllerMap[$id],$id,$owner===$this?null:$owner),
                        $this->parseActionParams($route),
                    );
                }

                // 看看当前应用的modules配置项中是否有以$id为key的模块，或当前模块的modules配置中是否有以$id为key的子模块，如果有则以$module为$owner参数值递归调用createController方法
                if(($module=$owner->getModule($id))!==null)
                    return $this->createController($route,$module);
                
                // 当前应用或模块下的控制器类的存放目录
                $basePath=$owner->getControllerPath();
                $controllerID='';
            }
            else
                $controllerID.='/';
            // 默认以$id为controller的ID，在当前应用或模块下查找是否有对应的控制器类文件
            $className=ucfirst($id).'Controller';
            $classFile=$basePath.DIRECTORY_SEPARATOR.$className.'.php';

            // 擦，怎么多出一个命名空间的东西？
            if($owner->controllerNamespace!==null)
                $className=$owner->controllerNamespace.'\\'.$className;
            // 如果有对应的控制器类文件，则尝试加载实例化
            if(is_file($classFile))
            {
                if(!class_exists($className,false))
                    require($classFile);
                if(class_exists($className,false) && is_subclass_of($className,'CController'))
                {
                    $id[0]=strtolower($id[0]);
                    return array(
                        new $className($controllerID.$id,$owner===$this?null:$owner),
                        $this->parseActionParams($route),
                    );
                }
                return null;
            }
            // 否则把$id看成普通的一级目录名
            $controllerID.=$id;
            $basePath.=DIRECTORY_SEPARATOR.$id;
        }
    }

从上述代码中可以看到，控制器类在实例化时需要传入该控制器类属于应用还是属于某个模块，这个归属记录在控制器类实例的_module属性中，如果属性值为null，则表示属于应用，_module属性定义于类`CController`中。

我们来看看上述代码中调用的方法`getModule`的实现，这个方法调用的`$owner`可能是应用对象也可能是某个模块类对象，该方法定义于抽象类`CModule`中，实现如下：

    :::php
    public function getModule($id)
    {
        // 如果$id对应的module已经实例化好，则直接返回
        if(isset($this->_modules[$id]) || array_key_exists($id,$this->_modules))
            return $this->_modules[$id];
        // 看是否配置了$id对应的module
        elseif(isset($this->_moduleConfig[$id]))
        {
            $config=$this->_moduleConfig[$id];
            if(!isset($config['enabled']) || $config['enabled'])
            {
                Yii::trace("Loading \"$id\" module",'system.base.CModule');
                $class=$config['class'];
                unset($config['class'], $config['enabled']);
                // 实例化module，module的$owner可能是当前应用对象，也可能是一个模块对象
                if($this===Yii::app())
                    $module=Yii::createComponent($class,$id,null,$config);
                else
                    $module=Yii::createComponent($class,$this->getId().'/'.$id,$this,$config);
                return $this->_modules[$id]=$module;
            }
        }
    }

从上述代码可以看到，每个模块对象也会记录它的归属 - 属于应用对象，还是某个父模块对象。

自定义模块类无需定义自己的构造方法，构造方法可以间接继承自抽象类`CModule`（`CWebModule`类并未定义自己的构造方法），其构造方法实现如下：

    :::php
    public function __construct($id,$parent,$config=null)
    {
        $this->_id=$id;
        $this->_parentModule=$parent;

        // set basePath at early as possible to avoid trouble
        if(is_string($config))
            $config=require($config);
        if(isset($config['basePath']))
        {
            $this->setBasePath($config['basePath']);
            unset($config['basePath']);
        }
        Yii::setPathOfAlias($id,$this->getBasePath());

        $this->preinit();

        $this->configure($config);
        $this->attachBehaviors($this->behaviors);
        $this->preloadComponents();

        $this->init();
    }

这个方法与Web应用类的构造方法（定义于抽象类`CApplication`中）实现非常相似。这两个构造方法是调用同一个`configure`方法来加载配置的，所以很多“应用”的配置项，“模块”也都支持。
从上述模块的构造方法中可以看到当前模块属于哪个父模块是记录在属性`_parentModule`中的，如果该属性值为null，则表示当前模块属于当前Web应用对象。这样通过获取控制器对象的`_module`属性值，继而获取模块对象的`_parentModule`属性值，就能知道整个归属关系链。

------

注：*以下部分是对[Yii源码阅读笔记 - 请求处理基本流程](http://youngsterxyf.github.io/2014/11/04/read-yii-code-1/)一文的补充。*

前面讨论的方法`createController`中还调用了方法`parseActionParams`来解析获取Action的ID，也定义于类`CWebApplication`中，实现如下：

    :::php
    /**
     * Parses a path info into an action ID and GET variables.
     * @param string $pathInfo path info
     * @return string action ID
     */
    protected function parseActionParams($pathInfo)
    {
        // 屌！其实就是以斜杠分割$pathInfo取第一个部分作为Action的ID
        if(($pos=strpos($pathInfo,'/'))!==false)
        {
            $manager=$this->getUrlManager();
            // 第一个部分之外剩余的部分做请求参数解析
            $manager->parsePathInfo((string)substr($pathInfo,$pos+1));
            
            $actionID=substr($pathInfo,0,$pos);
            return $manager->caseSensitive ? $actionID : strtolower($actionID);
        }
        else
            // 如果$pathInfoH中不存在斜杠，则就将$pathInfo作为Action的ID
            return $pathInfo;
    }

其中调用的`parsePathInfo`方法，定义于类`CUrlManager`中，实现如下：

    :::php
    /**
     * Parses a path info into URL segments and saves them to $_GET and $_REQUEST.
     * @param string $pathInfo path info
     */
    public function parsePathInfo($pathInfo)
    {
        if($pathInfo==='')
            return;
        $segs=explode('/',$pathInfo.'/');
        $n=count($segs);
        for($i=0;$i<$n-1;$i+=2)
        {
            $key=$segs[$i];
            if($key==='') continue;
            $value=$segs[$i+1];
            if(($pos=strpos($key,'['))!==false && ($m=preg_match_all('/\[(.*?)\]/',$key,$matches))>0)
            {
                $name=substr($key,0,$pos);
                for($j=$m-1;$j>=0;--$j)
                {
                    if($matches[1][$j]==='')
                        $value=array($value);
                    else
                        $value=array($matches[1][$j]=>$value);
                }
                if(isset($_GET[$name]) && is_array($_GET[$name]))
                    $value=CMap::mergeArray($_GET[$name],$value);
                $_REQUEST[$name]=$_GET[$name]=$value;
            }
            else
                $_REQUEST[$key]=$_GET[$key]=$value;
        }
    }

仔细看看上述代码的逻辑吧，累觉不爱啊！

这个方法的作用：在目标路由去除Controller ID和Action ID两个部分后，从剩余部分中按一定规则解析出请求参数，那么规则是什么样的呢？

举例来说，这个目标路由剩余部分的基本形式如下所示：

`key/value/key/value/`

其中`key`为参数名，`value`为参数值。

但`key`的形式可以数组取值的形式，如：

`name[x][y][z]`

这种形式的`key`对应的`value`会从原来的字符串转换成数组形式，如：

    :::php
    array(
        'x' => array(
            'y' => array(
                'z' => array('value')
            )
        )
    )

多个`key`的`name`可以相同，如果相同，则会合并数组。如：

`name[a][b][c]/value1/name[A][B][C]/value2/name[x][y][z]/value3/name[a][X][f]/value4/`

最终会转换成请求参数项：

    :::php
    $_REQUEST['name'] = $_GET['name'] = array(
        'a' => array(
            'b' => array(
                'c' => array('value1'),
            ),
            'X' => array(
                'f' => array('value4'),
            ),
        ),
        'A' => array(
            'B' => array(
                'C' => array('value2'),
            ),
        ),
        'x' => array(
            'y' => array(
                'z' => array('value3'),
            ),
        ),
    );

擦，牛逼到死啊！