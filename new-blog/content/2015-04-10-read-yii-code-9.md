Title: Yii源码阅读笔记 - 自定义类自动加载
Date: 2015-04-10
Author: youngsterxyf
Slug: read-yii-code-9
Tags: PHP, Yii, 笔记, 总结


前两天突然发现：之前的阅读笔记对于Yii应用中如何自动加载自定义类的问题没有解释。这里的自定义类是指非Yii框架本身的类。

关于组件类的配置加载已在 [Yii源码阅读笔记 - 组件集成](http://blog.xiayf.cn/2014/11/13/read-yii-code-3/) 一文中做了较为详细的说明，
所以这里不再涉及。

本文主要解释以下两点：

1. Yii框架是如何找到请求对应的自定义控制器类？
2. 在自定义控制器类中使用其他类（如Model类、或其他任意目录下文件中定义的类）时，Yii框架是如何自动加载的？

------

在 [Yii源码阅读笔记 - 应用模块化](http://blog.xiayf.cn/2014/11/20/read-yii-code-7/) 一文中介绍类 `CWebApplication` 中的方法 `createController` ，
该方法根据目标路由找到对应的控制器类文件并加载，方法中有行代码：

    :::php
    $basePath=$owner->getControllerPath();

这里的 `getControllerPath` 会返回当前应用或模块下的控制器类的存放目录，对应应用级与模块级，其实现有两处，其一是在类 `CWebApplication` 中：

    :::php
    /**
     * @return string the directory that contains the controller classes. Defaults to 'protected/controllers'.
     */
    public function getControllerPath()
    {
        if($this->_controllerPath!==null)
            return $this->_controllerPath;
        else
            return $this->_controllerPath=$this->getBasePath().DIRECTORY_SEPARATOR.'controllers';
    }

另一处是在类 `CWebModule` 中：

    :::php
    /**
     * @return string the directory that contains the controller classes. Defaults to 'moduleDir/controllers' where
     * moduleDir is the directory containing the module class.
     */
    public function getControllerPath()
    {
        if($this->_controllerPath!==null)
            return $this->_controllerPath;
        else
            return $this->_controllerPath=$this->getBasePath().DIRECTORY_SEPARATOR.'controllers';
    }

这两处实现的逻辑是一样的：如果属性 `_controllerPath` 未赋值，则**默认**以应用或模块目录下的**controllers**子目录作为自定义控制器类的存放目录。

如果不想以该路径作为自定义控制器类的存放目录，那么就得为 `_controllerPath` 赋值 - 与 `getControllerPath` 对应的有方法 `setControllerPath` （同样有两处定义，实现一样）：

    :::php
    /**
     * @param string $value the directory that contains the controller classes.
     * @throws CException if the directory is invalid
     */
    public function setControllerPath($value)
    {
        if(($this->_controllerPath=realpath($value))===false || !is_dir($this->_controllerPath))
            throw new CException(Yii::t('yii','The controller path "{path}" is not a valid directory.',
                array('{path}'=>$value)));
    }

从 `getControllerPath` 和 `setControllerPath` 的命名上就能知道这两个方法是分别由魔术方法 `__get` 和 `__set` 间接调用的。由 [Yii源码阅读笔记 - 请求处理基本流程](http://blog.xiayf.cn/2014/11/04/read-yii-code-1/) 一文内容可知，配置初始化的时候会调用类 `CModule` 的方法 `configure` ，该方法中又会触发魔术方法 `__set` 。这也就意味着可以在应用配置中添加 `controllerPath` 一项来声明自定义控制器类的存放目录。

------

那么当自定义控制类中使用Model类或者其他辅助类时，Yii是如何自动加载的呢？

以 **在控制器类中IndexController调用Model类UserModel的getUserInfo方法获取用户信息** 为例，Yii是怎么找到并加载UserModel类文件的呢？

在 [Yii源码阅读笔记 - 请求处理基本流程](http://blog.xiayf.cn/2014/11/04/read-yii-code-1/) 一文的最后提到 - 类文件yii/framework/YiiBase.php的倒数第二行代码为：

    :::php
    spl_autoload_register(array('YiiBase','autoload'));

在应用初始化时，类文件 `Yii.php` 中会require类文件 `YiiBase.php`，从而会执行该句代码，将YiiBase类的方法autoload注册到 `SPL __autoload` 函数队列中。

而类 YiiBase 的 autoload 方法实现如下：

    :::php
    /**
     * Class autoload loader.
     * This method is provided to be invoked within an __autoload() magic method.
     * @param string $className class name
     * @return boolean whether the class has been loaded successfully
     */
    public static function autoload($className)
    {
        // use include so that the error PHP file may appear
        // 先在 $classMap 中查找
        if(isset(self::$classMap[$className]))
            include(self::$classMap[$className]);
        // 在 $_coreClasses 中查找
        elseif(isset(self::$_coreClasses[$className]))
            include(YII_PATH.self::$_coreClasses[$className]);
        else
        {
            // 如果 $className 不带 命名空间
            // include class file relying on include_path
            if(strpos($className,'\\')===false)  // class without namespace
            {
                if(self::$enableIncludePath===false)
                {
                    foreach(self::$_includePaths as $path)
                    {
                        $classFile=$path.DIRECTORY_SEPARATOR.$className.'.php';
                        if(is_file($classFile))
                        {
                            include($classFile);
                            if(YII_DEBUG && basename(realpath($classFile))!==$className.'.php')
                                throw new CException(Yii::t('yii','Class name "{class}" does not match class file "{file}".', array(
                                    '{class}'=>$className,
                                    '{file}'=>$classFile,
                                )));
                            break;
                        }
                    }
                }
                else
                    include($className.'.php');
            }
            // $className 带 命名空间
            else  // class name with namespace in PHP 5.3
            {
                $namespace=str_replace('\\','.',ltrim($className,'\\'));
                if(($path=self::getPathOfAlias($namespace))!==false)
                    include($path.'.php');
                else
                    return false;
            }
            return class_exists($className,false) || interface_exists($className,false);
        }
        return true;
    }

上述代码中涉及的 `self::$_coreClasses` 属性定义于类 YiiBase，其中罗列了Yii框架核心类的名称与相对路径。

属性 `self::$_classMap` ，默认是一个空数组，在类 YiiBase 的静态方法 import 中根据条件可能被赋予元素；属性 `self::$_includePaths` 也是如此，只不过默认未赋值。静态方法 `import` 实现如下所示：

    :::php
    public static function import($alias,$forceInclude=false)
    {
        if(isset(self::$_imports[$alias]))  // previously imported
            return self::$_imports[$alias];

        if(class_exists($alias,false) || interface_exists($alias,false))
            return self::$_imports[$alias]=$alias;

        // 带 命名空间
        if(($pos=strrpos($alias,'\\'))!==false) // a class name in PHP 5.3 namespace format
        {
            $namespace=str_replace('\\','.',ltrim(substr($alias,0,$pos),'\\'));
            if(($path=self::getPathOfAlias($namespace))!==false)
            {
                $classFile=$path.DIRECTORY_SEPARATOR.substr($alias,$pos+1).'.php';

                // 默认为false的哦
                if($forceInclude)
                {
                    if(is_file($classFile))
                        require($classFile);
                    else
                        throw new CException(Yii::t('yii','Alias "{alias}" is invalid. Make sure it points to an existing PHP file and the file is readable.',array('{alias}'=>$alias)));
                    self::$_imports[$alias]=$alias;
                }
                else
                    self::$classMap[$alias]=$classFile;
                return $alias;
            }
            else
            {
                // try to autoload the class with an autoloader
                if (class_exists($alias,true))
                    return self::$_imports[$alias]=$alias;
                else
                    throw new CException(Yii::t('yii','Alias "{alias}" is invalid. Make sure it points to an existing directory or file.',
                        array('{alias}'=>$namespace)));
            }
        }

        // 从后往前第一个 . 的位置
        if(($pos=strrpos($alias,'.'))===false)  // a simple class name
        {
            if($forceInclude && self::autoload($alias))
                self::$_imports[$alias]=$alias;
            return $alias;
        }

        // 取类名部分
        $className=(string)substr($alias,$pos+1);
        // 如果类名为 * 则表示非类文件，而是目录
        $isClass=$className!=='*';

        if($isClass && (class_exists($className,false) || interface_exists($className,false)))
            return self::$_imports[$alias]=$className;

        if(($path=self::getPathOfAlias($alias))!==false)
        {
            // 类文件
            if($isClass)
            {
                if($forceInclude)
                {
                    if(is_file($path.'.php'))
                        require($path.'.php');
                    else
                        throw new CException(Yii::t('yii','Alias "{alias}" is invalid. Make sure it points to an existing PHP file and the file is readable.',array('{alias}'=>$alias)));
                    self::$_imports[$alias]=$className;
                }
                else
                    self::$classMap[$className]=$path.'.php';
                return $className;
            }
            // 目录
            else  // a directory
            {
                if(self::$_includePaths===null)
                {
                    self::$_includePaths=array_unique(explode(PATH_SEPARATOR,get_include_path()));
                    if(($pos=array_search('.',self::$_includePaths,true))!==false)
                        unset(self::$_includePaths[$pos]);
                }

                array_unshift(self::$_includePaths,$path);

                if(self::$enableIncludePath && set_include_path('.'.PATH_SEPARATOR.implode(PATH_SEPARATOR,self::$_includePaths))===false)
                    self::$enableIncludePath=false;

                return self::$_imports[$alias]=$path;
            }
        }
        else
            throw new CException(Yii::t('yii','Alias "{alias}" is invalid. Make sure it points to an existing directory or file.',
                array('{alias}'=>$alias)));
    }

静态方法import在类CModule（CWebApplication类间接继承自该类）的方法 `setImport` 中会被调用（当然还有其他地方也会调用import方法）：

    :::php
    /**
     * Sets the aliases that are used in the module.
     * @param array $aliases list of aliases to be imported
     */
    public function setImport($aliases)
    {
        foreach($aliases as $alias)
            Yii::import($alias);
    }

看到前缀为`set`，就知道魔术方法 `__set` 能间接调用该方法，如前所述，可以为应用提供名为 **import** 的配置项。例如目前我们项目中有import配置项如下所示：

    :::php
    'import'=>array(
        'application.models.*',
        'application.components.*',
    )

表示业务逻辑的代码（如自定义控制器类）中会使用到应用的子目录models和components下的类文件，需要Yii（准确地说是YiiBase类autoload方法）帮忙自动查找加载。
这样也就能任意组织项目的目录结构（**当然不要太任性！**）。

import配置项的值是一个路径别名数组，路径别名中的application表示应用的根目录，默认为与index.php同一级的protected目录，也可以通过配置项basePath来指定。对于basePath配置项，在类CApplication的构造方法 `__contruct` 中有如下相关代码：

    :::php
    if(isset($config['basePath']))
    {
        $this->setBasePath($config['basePath']);
        unset($config['basePath']);
    }
    else
        $this->setBasePath('protected');
    Yii::setPathOfAlias('application',$this->getBasePath());

其中方法 `setPathAlias` 的实现如下所示：

    :::php
    public static function setPathOfAlias($alias,$path)
    {
        if(empty($path))
            unset(self::$_aliases[$alias]);
        else
            self::$_aliases[$alias]=rtrim($path,'\\/');
    }

------

除了通过import配置项指定autoload的查找路径，从类YiiBase的autoload方法实现可以看到，对于PHP 5.3以上版本，可以使用命名空间的方式来自动查找类，命名空间字符串会被替换成路径别名，所以命名空间字符串应以 `application\` 开始，如应这样 `application\models\UserModel` 来引用models目录下的UserModel类文件，除非额外通过 `Yii::setPathOfAlias`为models路径指定别名。

另外，类YiiBase中提供了一个静态方法 `registerAutoloader` ：

    :::php
    /**
     * Registers a new class autoloader.
     * The new autoloader will be placed before {@link autoload} and after
     * any other existing autoloaders.
     * @param callback $callback a valid PHP callback (function name or array($className,$methodName)).
     * @param boolean $append whether to append the new autoloader after the default Yii autoloader.
     * Be careful using this option as it will disable {@link enableIncludePath autoloading via include path}
     * when set to true. After this the Yii autoloader can not rely on loading classes via simple include anymore
     * and you have to {@link import} all classes explicitly.
     */
    public static function registerAutoloader($callback, $append=false)
    {
        if($append)
        {
            self::$enableIncludePath=false;
            spl_autoload_register($callback);
        }
        else
        {
            spl_autoload_unregister(array('YiiBase','autoload'));
            spl_autoload_register($callback);
            spl_autoload_register(array('YiiBase','autoload'));
        }
    }

可通过该静态方法针对项目的目录结构添加一个自定义的自动查找加载方式。


#### 参考资料

- [PHP手册 - spl_autoload_register](http://php.net/manual/zh/function.spl-autoload-register.php)
