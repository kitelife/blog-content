Title: Yii源码阅读笔记 - 模板引擎集成
Date: 2014-11-18
Author: youngsterxyf
Slug: read-yii-code-5
Tags: PHP, Yii, 笔记, 总结


### 概述

通常我们会使用模板引擎来渲染HTML页面，而不是使用HTML代码中插入PHP代码的方式来编写动态页面。Yii框架中模板引擎也是作为组件引入的，默认ID为viewRenderer，
但从[Yii源码阅读笔记 - 组件集成](http://youngsterxyf.github.io/2014/11/13/read-yii-code-3/)可以看到Yii Web应用加载的核心组件中并没有viewRenderer，所以需要自己配置。
Yii提供了一个直接可用的模板引擎组件类CPradoViewRenderer（见文件`yii/framework/web/renderers/CPradoViewRenderer.php`），该模板引擎类让开发者可以使用类Prado框架的模板语法。

如果你想使用Smarty这种第三方模板引擎，有两种方式将模板引擎引入Yii中使用（以Smarty为例）：

1. 将Smarty封装成一个Yii的普通组件，然后配置加载到Yii::app()。假设组件ID为smarty，那么就可以通过`Yii::app()->smarty`来调用组件。
2. 参考CPradoViewRenderer类的实现，将Smarty封装成一个模板引擎组件，并以ID为viewRenderer进行配置加载。

相比而言，第二种方式更好。原因是：第一种方式由于每种第三方模板引擎的接口不一样，如果应用要替换模板引擎，就需要修改控制器类中的代码。而第二种方式由于第三方组件统一封装成Yii框架定义的模板引擎接口形式，
所以如果要替换模板引擎，只需修改自定义模板引擎组件类的接口实现就可以了。这样调用模板引擎的代码逻辑就只依赖接口形式，而不是依赖于接口实现，从而实现解耦。

本文主要分析第二种方式的实现。

### 分析

Yii中对页面模板进行渲染可以调用`CController`类（见文件`yii/framework/web/CController.php`）的方法`render`，实现如下：

    :::php
    /**
     * Renders a view with a layout.
     *
     * This method first calls {@link renderPartial} to render the view (called content view).
     * It then renders the layout view which may embed the content view at appropriate place.
     * In the layout view, the content view rendering result can be accessed via variable
     * <code>$content</code>. At the end, it calls {@link processOutput} to insert scripts
     * and dynamic contents if they are available.
     *
     * By default, the layout view script is "protected/views/layouts/main.php".
     * This may be customized by changing {@link layout}.
     *
     * @param string $view name of the view to be rendered. See {@link getViewFile} for details
     * about how the view script is resolved.
     * @param array $data data to be extracted into PHP variables and made available to the view script
     * @param boolean $return whether the rendering result should be returned instead of being displayed to end users.
     * @return string the rendering result. Null if the rendering result is not required.
     * @see renderPartial
     * @see getLayoutFile
     */
    public function render($view,$data=null,$return=false)
    {
        // beforeRender默认返回true，
        // 可以在自定义controller类中重写该方法，实现渲染之前的预处理
        // 但和beforeAction一样，应该要返回true或false
        if($this->beforeRender($view))
        {
            // 渲染真正的内容部分
            $output=$this->renderPartial($view,$data,true);
            // 获取布局文件
            if(($layoutFile=$this->getLayoutFile($this->layout))!==false)
                // 渲染整个页面
                $output=$this->renderFile($layoutFile,array('content'=>$output),true);

            // 渲染的后处理，默认为空，在processOutput之前调用
            $this->afterRender($view,$output);

            // 对渲染结果进行处理
            $output=$this->processOutput($output);

            // 可以将渲染结果作为方法的返回值返回，或者直接输出到用户浏览器
            if($return)
                return $output;
            else
                echo $output;
        }
    }

其中方法renderPartial的实现如下所示：

    :::php
    /**
     * Renders a view.
     *
     * The named view refers to a PHP script (resolved via {@link getViewFile})
     * that is included by this method. If $data is an associative array,
     * it will be extracted as PHP variables and made available to the script.
     *
     * This method differs from {@link render()} in that it does not
     * apply a layout to the rendered result. It is thus mostly used
     * in rendering a partial view, or an AJAX response.
     *
     * @param string $view name of the view to be rendered. See {@link getViewFile} for details
     * about how the view script is resolved.
     * @param array $data data to be extracted into PHP variables and made available to the view script
     * @param boolean $return whether the rendering result should be returned instead of being displayed to end users
     * @param boolean $processOutput whether the rendering result should be postprocessed using {@link processOutput}.
     * @return string the rendering result. Null if the rendering result is not required.
     * @throws CException if the view does not exist
     * @see getViewFile
     * @see processOutput
     * @see render
     */
    public function renderPartial($view,$data=null,$return=false,$processOutput=false)
    {
        // 获取目标模板文件
        $viewFile=$this->getViewFile($view);
        echo (basename(__FILE__).':'.__LINE__.':'.__FUNCTION__.'() $viewFile '. var_export($viewFile, true));
        if(($viewFile)!==false)
        {
            // 渲染
            $output=$this->renderFile($viewFile,$data,true);
            // 如果$processOutput为真，则也会对结果进行后处理
            if($processOutput)
                $output=$this->processOutput($output);
            if($return)
                return $output;
            else
                echo $output;
        }
        else
            throw new CException(Yii::t('yii','{controller} cannot find the requested view "{view}".',
                array('{controller}'=>get_class($this), '{view}'=>$view)));
    }

`renderPartial`方法并不会渲染出一个完整的页面，只是渲染页面的一部分，通常是主体部分，或者为AJAX请求渲染出响应结果。
其中调用的getViewFile方法实现如下：

    :::php
    public function getViewFile($viewName)
    {
        // 如果未配置theme项，即表示不使用theme，那么getTheme方法返回null
        if(($theme=Yii::app()->getTheme())!==null && ($viewFile=$theme->getViewFile($this,$viewName))!==false)
            return $viewFile;
        // viewPath默认为views，可配置
        $moduleViewPath=$basePath=Yii::app()->getViewPath();
        echo (basename(__FILE__).':'.__LINE__.':'.__FUNCTION__.'() $moduleViewPath '. var_export($moduleViewPath, true)),"\n";
        // 模块化，如果没有，则getModule返回null
        if(($module=$this->getModule())!==null)
            $moduleViewPath=$module->getViewPath();
        // $this->getViewPath()得到的路径相比$moduleViewPath就是多了controller的ID一级
        return $this->resolveViewFile($viewName,$this->getViewPath(),$basePath,$moduleViewPath);
    }

代码中`$this->getViewPath()`方法的实现如下：

    :::php
    public function getViewPath()
    {
        if(($module=$this->getModule())===null)
            $module=Yii::app();
        // $this->getId()是得到当前controller的ID，这个ID是在controller实例化时构造方法中赋值给属性_id的。
        // 这也就意味着页面模板文件需要按照controller的ID分目录存放
        return $module->getViewPath().DIRECTORY_SEPARATOR.$this->getId();
    }

`getViewFile`中最后调用的方法`resolveViewFile`实现如下所示：

    :::php
    public function resolveViewFile($viewName,$viewPath,$basePath,$moduleViewPath=null)
    {
        // 连模板文件名都不给，还玩个屁啊
        if(empty($viewName))
            return false;

        // 若$moduleViewPath未设置，则在应用的页面模板的根目录下找
        if($moduleViewPath===null)
            $moduleViewPath=$basePath;

        // 获取设置的模板渲染引擎，其实就是加载ID为viewRenderer的组件
        if(($renderer=Yii::app()->getViewRenderer())!==null)
            // 模板文件的扩展类型默认为'.php'，可配置
            $extension=$renderer->fileExtension;
        else
            $extension='.php';
        echo (basename(__FILE__).':'.__LINE__.':'.__FUNCTION__.'() $extension '. var_export($extension, true)),"\n";
        // 如果指定的模板文件名以/开始
        if($viewName[0]==='/')
        {
            // 如果指定的模板文件名以//开始，则表示在模板的根目录下查找
            if(strncmp($viewName,'//',2)===0)
                $viewFile=$basePath.$viewName;
            // 否则（以单个/开始）在模块的模板目录下查找
            else
                $viewFile=$moduleViewPath.$viewName;
        }
        // 如果模板文件名中存在.且.不出现在第一个位置，则认为这是一个路径别名，需要转换真正的路径
        elseif(strpos($viewName,'.'))
            $viewFile=Yii::getPathOfAlias($viewName);
        else
            // 否则在当前controller的模板目录下找
            $viewFile=$viewPath.DIRECTORY_SEPARATOR.$viewName;

        // 可能站点是需要国际化的
        // 所以在找到默认的模板文件后，尝试找一下对应用户目标语言的模板文件
        if(is_file($viewFile.$extension))
            return Yii::app()->findLocalizedFile($viewFile.$extension);
        // 如果不存在指定扩展类型的模板文件，且扩展类型不为'.php'，则看一下'.php'类型的模板文件是否存在
        elseif($extension!=='.php' && is_file($viewFile.'.php'))
            return Yii::app()->findLocalizedFile($viewFile.'.php');
        else
            return false;
    }

方法`resolveViewFile`中最后调用的方法`findLocalizedFile`，定义于抽象类CApplication中，实现如下：

    :::php
    public function findLocalizedFile($srcFile,$srcLanguage=null,$language=null)
    {
        if($srcLanguage===null)
            // sourceLanguage为public的属性，可配置，默认为en_us
            $srcLanguage=$this->sourceLanguage;
        if($language===null)
            // getLanguage的实现：$this->_language===null ? $this->sourceLanguage : $this->_language
            // 默认_language为未赋值，即null，所以取到的还是sourceLanguage属性值。
            // 但因为__set，所以也是可赋值的，这个赋值不应该是配置造成的，应该是根据用户的cookie中指定的语言选项，在请求处理时设置的，表示用户的目标语言
            $language=$this->getLanguage();
        // 如果用户的目标语言（或者用户选择的是默认语言），则直接返回默认模板文件的路径
        if($language===$srcLanguage)
            return $srcFile;
        // 否则取到对应目标语言的模板文件
        $desiredFile=dirname($srcFile).DIRECTORY_SEPARATOR.$language.DIRECTORY_SEPARATOR.basename($srcFile);
        // 如果对应目标语言的模板文件不存在，则还是返回默认的模板文件
        return is_file($desiredFile) ? $desiredFile : $srcFile;
    }

从上述模板文件的寻找过程可以看到，最后返回的目标模板文件的路径是一个相对路径，以动态脚本根目录（默认为protected）开始。

方法`renderPartial`中在得到目标模板文件相对路径后，即调用renderFile方法（定义于CBaseController类中）来渲染模板，该方法的实现如下：

    :::php
    public function renderFile($viewFile,$data=null,$return=false)
    {
        $widgetCount=count($this->_widgetStack);
        // Yii::app()->getViewRenderer() 获取模板引擎组件
        if(($renderer=Yii::app()->getViewRenderer())!==null && $renderer->fileExtension==='.'.CFileHelper::getExtension($viewFile))
            $content=$renderer->renderFile($this,$viewFile,$data,$return);
        else
            // 如果没法用模板引擎来渲染（可能不是模板引擎的目标模板，也可能是没设置模板引擎组件），则当前普通的PHP文件（HTML代码中夹杂着PHP代码）来渲染
            $content=$this->renderInternal($viewFile,$data,$return);
        if(count($this->_widgetStack)===$widgetCount)
            return $content;
        else
        {
            $widget=end($this->_widgetStack);
            throw new CException(Yii::t('yii','{controller} contains improperly nested widget tags in its view "{view}". A {widget} widget does not have an endWidget() call.',
                array('{controller}'=>get_class($this), '{view}'=>$viewFile, '{widget}'=>get_class($widget))));
        }
    }

`renderFile`中`$content=$renderer->renderFile($this,$viewFile,$data,$return);`一行调用的renderFile方法，在抽象类CViewRenderer中定义如下：

    :::php
    public function renderFile($context,$sourceFile,$data,$return)
    {
        if(!is_file($sourceFile) || ($file=realpath($sourceFile))===false)
            throw new CException(Yii::t('yii','View file "{file}" does not exist.',array('{file}'=>$sourceFile)));
        // 尝试从runtime目录中获取已编译好的模板，如果编译好的模板不是同一存放在runtime目录下，则默认和未编译的模板文件在同一个目录下，并且文件名多一个"c"后缀
        // 得到$viewFile可能并不存在，第一次请求该模板
        $viewFile=$this->getViewFile($sourceFile);
        // 如果相比已编译好的模板文件，未编译的模板已发生变更，则需要重新编译
        // 如果已编译好的模板文件不存在，则@filemtime($viewFile)返回的是false，这个条件也是返回true
        if(@filemtime($sourceFile)>@filemtime($viewFile))
        {
            // 抽象类CViewRenderer中generateViewFile方法并未实现，所以自己封装模板引擎组件时需要实现该方法
            $this->generateViewFile($sourceFile,$viewFile);
            // 设置编译好的模板文件的访问权限，默认是0755 (owner rwx, group rx and others rx)
            @chmod($viewFile,$this->filePermission);
        }
        // 编译好的模板文件其实就是一个PHP脚本（HTML代码中夹杂PHP代码），所以还需要渲染一下
        return $context->renderInternal($viewFile,$data,$return);
    }

类`CController`的`render`方法在调用`renderPartial`得到渲染结果后，取得页面布局模板文件，然后将`renderPartial`的渲染结果作为数据渲染布局模板，从而得到一个完整HTML页面。
获取布局模板文件路径的方法`getLayoutFile`实现如下所示（定义于类CController中）：

    :::php
    public function getLayoutFile($layoutName)
    {
        if($layoutName===false)
            return false;
        if(($theme=Yii::app()->getTheme())!==null && ($layoutFile=$theme->getLayoutFile($this,$layoutName))!==false)
            return $layoutFile;

        if(empty($layoutName))
        {
            $module=$this->getModule();
            // 递归向父级模板查找布局文件
            while($module!==null)
            {
                if($module->layout===false)
                    return false;
                if(!empty($module->layout))
                    break;
                $module=$module->getParentModule();
            }
            // 如果当前controller不属于某个module
            if($module===null)
                $module=Yii::app();
            // 默认为main，可配置
            $layoutName=$module->layout;
        }
        elseif(($module=$this->getModule())===null)
            $module=Yii::app();

        return $this->resolveViewFile($layoutName,$module->getLayoutPath(),Yii::app()->getViewPath(),$module->getViewPath());
    }

其逻辑与方法`getViewFile`类似。

------

由上述分析可知，将第三方模板引擎封装成Yii框架的模板引擎组件，可以继承自抽象类`CViewRenderer`，并实现其方法`generateViewFile`，然后配置该组件的ID为`viewRenderer`。
对于模板文件的存放，需要考虑Web应用是否分模块、应用是否国际化、模板文件相关controller的ID等，模板文件名的扩展类型应与模板引擎组件配置的一样。