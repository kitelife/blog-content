Title: Yii源码阅读笔记 - 错误/异常处理
Date: 2015-09-14
Author: youngsterxyf
Slug: read-yii-code-10
Tags: PHP, Yii, 笔记, 总结


### 概述

PHP区分“错误”（Error）和“异常”（Exception）。“错误”通常是由PHP内部函数抛出，表示运行时问题，当然也可以通过函数trigger_error或user_error抛出一个用户级别的error/warning/notice信息。但在引入面向对象之后，相比使用trigger_error抛出错误，使用throw抛出异常更常用。

对于“错误”，PHP允许配置报告哪些级别/类型错误、是否（向用户）展示错误、是否对错误记录日志、错误日志记到哪，分别对应php.ini中的配置项：error_reporting、display_errors、log_errors、error_log。详细信息见[这里](http://php.net/manual/zh/language.errors.basics.php)。

对于应用程序内层调用抛出的“异常”，一般可以在外层中使用try...catch来捕获并自定义处理过程。但对于“错误”（PHP运行时抛出或者应用程序使用trigger_error抛出的）或者对于-无法使用try...catch来捕获可能的异常/为了做到即使忘记捕获的异常也能得到自定义处理-的情况，该怎么办？对此，PHP提供了函数`set_error_handler`和`set_exception_handler`来注册错误/异常自定义处理过程。如果在程序的执行流中先后多次调用了`set_error_handler`或`set_exception_handler`，后一次注册的处理过程会覆盖前一次的，但可以通过函数`restore_error_handler`或`restore_exception_handler`来恢复前一次注册的异常处理过程。

*之所以写这篇文章，是因为最近在工作中犯了一个低级错误：应用程序中有个API对于不合法的请求参数直接抛出异常（`throw new Exception("xxx")`），却忘了try...catch捕捉，导致异常被Yii框架（我们的应用基于Yii开发）通过set_exception_handler注册的方法处理 - 响应500，之后这个API被一个扫描器拼命扫，导致出现500多的响应，触发了告警。*

### 分析

我们来看看Yii框架在哪个地方注册错误/异常处理过程？处理过程是什么样的？

Yii框架在请求处理初始化过程中，在`CApplication`类（见文件`base/CApplication.php`）的构造方法中调用了：

```php
<?php
$this->initSystemHandlers();
```

`initSystemHandlers`的实现如下：

```php
<?php
/**
 * Initializes the class autoloader and error handlers.
 */
protected function initSystemHandlers()
{
	// 注：如果不想使用Yii框架注册的handleException，可以在初始化应用实例之前，定义常量YII_ENABLE_EXCEPTION_HANDLER值为false
	if(YII_ENABLE_EXCEPTION_HANDLER)
		set_exception_handler(array($this,'handleException'));
	// 注：YII_ENABLE_ERROR_HANDLER也是如此
	if(YII_ENABLE_ERROR_HANDLER)
		set_error_handler(array($this,'handleError'),error_reporting());
}
```

其中注册的方法`handleException`和`handleError`实现分别如下：

```php
<?php
public function handleException($exception)
{
	// disable error capturing to avoid recursive errors
	// 这句注释是啥意思？
	restore_error_handler();
	restore_exception_handler();

	// 生成并记录日志信息
	$category='exception.'.get_class($exception);
	if($exception instanceof CHttpException)
		$category.='.'.$exception->statusCode;
	// php <5.2 doesn't support string conversion auto-magically
	$message=$exception->__toString();
	if(isset($_SERVER['REQUEST_URI']))
		$message.="\nREQUEST_URI=".$_SERVER['REQUEST_URI'];
	if(isset($_SERVER['HTTP_REFERER']))
		$message.="\nHTTP_REFERER=".$_SERVER['HTTP_REFERER'];
	$message.="\n---";
	Yii::log($message,CLogger::LEVEL_ERROR,$category);

	try
	{
		// 将异常封装成事件，并触发事件，从而触发监听该事件的处理过程
		$event=new CExceptionEvent($this,$exception);
		$this->onException($event);
		// 如果事件并没有被处理（即没有监听该事件的处理过程）或者所有处理过程都没有将事件的handled属性置为true，则还得自己处理一下
		if(!$event->handled)
		{
			// try an error handler
			if(($handler=$this->getErrorHandler())!==null)
				$handler->handle($event);
			else
				$this->displayException($exception);
		}
	}
	catch(Exception $e)
	{
		$this->displayException($e);
	}

	try
	{
		// 尝试触发onEndRequest事件
		$this->end(1);
	}
	catch(Exception $e)
	{
		// use the most primitive way to log error
		$msg = get_class($e).': '.$e->getMessage().' ('.$e->getFile().':'.$e->getLine().")\n";
		$msg .= $e->getTraceAsString()."\n";
		$msg .= "Previous exception:\n";
		$msg .= get_class($exception).': '.$exception->getMessage().' ('.$exception->getFile().':'.$exception->getLine().")\n";
		$msg .= $exception->getTraceAsString()."\n";
		$msg .= '$_SERVER='.var_export($_SERVER,true);
		error_log($msg);
		exit(1);
	}
}
```

```php
<?php
public function handleError($code,$message,$file,$line)
{
	if($code & error_reporting())
	{
		// disable error capturing to avoid recursive errors
		restore_error_handler();
		restore_exception_handler();

		// 生成并记录日志信息
		$log="$message ($file:$line)\nStack trace:\n";
		
		// debug_backtrace() 产生一条 PHP 的回溯跟踪
		$trace=debug_backtrace();
		// skip the first 3 stacks as they do not tell the error position
		if(count($trace)>3)
			$trace=array_slice($trace,3);
		foreach($trace as $i=>$t)
		{
			if(!isset($t['file']))
				$t['file']='unknown';
			if(!isset($t['line']))
				$t['line']=0;
			if(!isset($t['function']))
				$t['function']='unknown';
			$log.="#$i {$t['file']}({$t['line']}): ";
			if(isset($t['object']) && is_object($t['object']))
				$log.=get_class($t['object']).'->';
			$log.="{$t['function']}()\n";
		}
		if(isset($_SERVER['REQUEST_URI']))
			$log.='REQUEST_URI='.$_SERVER['REQUEST_URI'];
		Yii::log($log,CLogger::LEVEL_ERROR,'php');

		try
		{
			// 将错误封装成事件，并触发
			Yii::import('CErrorEvent',true);
			$event=new CErrorEvent($this,$code,$message,$file,$line);
			$this->onError($event);
			// 如果错误事件未被处理
			if(!$event->handled)
			{
				// try an error handler
				if(($handler=$this->getErrorHandler())!==null)
					$handler->handle($event);
				else
					$this->displayError($code,$message,$file,$line);
			}
		}
		catch(Exception $e)
		{
			$this->displayException($e);
		}

		try
		{
			// 尝试触发onEndRequest事件
			$this->end(1);
		}
		catch(Exception $e)
		{
			// use the most primitive way to log error
			$msg = get_class($e).': '.$e->getMessage().' ('.$e->getFile().':'.$e->getLine().")\n";
			$msg .= $e->getTraceAsString()."\n";
			$msg .= "Previous error:\n";
			$msg .= $log."\n";
			$msg .= '$_SERVER='.var_export($_SERVER,true);
			error_log($msg);
			exit(1);
		}
	}
}
```

从上面代码可以看到，方法`handleException`的关键部分为：

```php
<?php
// 将异常封装成事件，并触发事件，从而触发监听该事件的处理过程
$event=new CExceptionEvent($this,$exception);
$this->onException($event);
// 如果事件并没有被处理（即没有监听该事件的处理过程）或者所有处理过程都没有将事件的handled属性置为true，则还得自己处理一下
if(!$event->handled)
{
	// try an error handler
	if(($handler=$this->getErrorHandler())!==null)
		$handler->handle($event);
	else
		$this->displayException($exception);
}
```

其中方法`onException`的实现如下：

```php
<?php
public function onException($event)
{
	$this->raiseEvent('onException',$event);
}
```

`raiseEvent`方法实现如下：

```php
<?php
public function raiseEvent($name,$event)
{
	// 根据事件名称，如onException，找到注册到该事件的处理过程，逐个触发调用。
	// 所有该事件注册的处理过程存放在$this->_e[$name]中
	$name=strtolower($name);
	if(isset($this->_e[$name]))
	{
		foreach($this->_e[$name] as $handler)
		{
			if(is_string($handler))
				call_user_func($handler,$event);
			elseif(is_callable($handler,true))
			{
				if(is_array($handler))
				{
					// an array: 0 - object, 1 - method name
					list($object,$method)=$handler;
					if(is_string($object))	// static method call
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
```

那么是如何注册事件的处理过程的呢？

在类`CComponent`（见文件`base/CComponent.php`，`CApplication`类继承间接继承自该类）中定义了一对方法：`attachEventHandler`（将处理过程绑定到某事件）和`detachEventHandler`（将处理过程从事件解绑）。

方法`attachEventHandler`的实现如下：

```php
<?php
public function attachEventHandler($name,$handler)
{
	$this->getEventHandlers($name)->add($handler);
}
```

其中`getEventHandlers`实现如下：

```php
<?php
public function getEventHandlers($name)
{
	// 可以关注一下方法hasEvent
	// 检查是否存在$name对应的事件
	if($this->hasEvent($name))
	{
		$name=strtolower($name);
		if(!isset($this->_e[$name]))
			$this->_e[$name]=new CList;
		// 返回对应事件的处理过程列表
		return $this->_e[$name];
	}
	else
		throw new CException(Yii::t('yii','Event "{class}.{event}" is not defined.',
			array('{class}'=>get_class($this), '{event}'=>$name)));
}
```

回到“方法`handleException`的关键部分”，在事件的handled属性没有置为true的情况下，会调用方法`getErrorHandler `取到内置的一个处理过程，该方法实现如下：

```php
<?php
public function getErrorHandler()
{
	// 获取名为errorHandler的组件，该组件默认会在CApplication类的registerCoreComponents方法中注册，
	// 见http://blog.xiayf.cn/2014/11/13/read-yii-code-3/一文的说明
	return $this->getComponent('errorHandler');
}
```

名为errorHandler的组件默认为类`CErrorHandler`（见文件`base/CErrorHandler.php`），当然也可以配置覆盖默认行为。

`CErrorHandler`类的`handle`方法实现如下：

```php
<?php
public function handle($event)
{
	// set event as handled to prevent it from being handled by other event handlers
	$event->handled=true;

	if($this->discardOutput)
	{
		$gzHandler=false;
		foreach(ob_list_handlers() as $h)
		{
			if(strpos($h,'gzhandler')!==false)
				$gzHandler=true;
		}
		// the following manual level counting is to deal with zlib.output_compression set to On
		// for an output buffer created by zlib.output_compression set to On ob_end_clean will fail
		for($level=ob_get_level();$level>0;--$level)
		{
			if(!@ob_end_clean())
				ob_clean();
		}
		// reset headers in case there was an ob_start("ob_gzhandler") before
		if($gzHandler && !headers_sent() && ob_list_handlers()===array())
		{
			if(function_exists('header_remove')) // php >= 5.3
			{
				header_remove('Vary');
				header_remove('Content-Encoding');
			}
			else
			{
				header('Vary:');
				header('Content-Encoding:');
			}
		}
	}
	
	// 异常和错误都可以调用handle方法
	if($event instanceof CExceptionEvent)
		$this->handleException($event->exception);
	else // CErrorEvent
		$this->handleError($event);
}
```

其中方法`handleException`和`handleError`实现分别如下：

```php
<?php
protected function handleException($exception)
{
	$app=Yii::app();
	// 如果是Web应用
	if($app instanceof CWebApplication)
	{
		if(($trace=$this->getExactTrace($exception))===null)
		{
			$fileName=$exception->getFile();
			$errorLine=$exception->getLine();
		}
		else
		{
			$fileName=$trace['file'];
			$errorLine=$trace['line'];
		}

		$trace = $exception->getTrace();

		foreach($trace as $i=>$t)
		{
			if(!isset($t['file']))
				$trace[$i]['file']='unknown';

			if(!isset($t['line']))
				$trace[$i]['line']=0;

			if(!isset($t['function']))
				$trace[$i]['function']='unknown';

			unset($trace[$i]['object']);
		}

		$this->_error=$data=array(
			// 如果抛出的异常是CHttpException类型，使用该异常自身的statusCode作为HTTP响应码，否则HTTP响应码为500
			// 所以在有意让Yii框架来处理抛出的异常时，需要明确指定异常的类型！
			'code'=>($exception instanceof CHttpException)?$exception->statusCode:500,
			'type'=>get_class($exception),
			'errorCode'=>$exception->getCode(),
			'message'=>$exception->getMessage(),
			'file'=>$fileName,
			'line'=>$errorLine,
			'trace'=>$exception->getTraceAsString(),
			'traces'=>$trace,
		);

		if(!headers_sent())
			header("HTTP/1.0 {$data['code']} ".$this->getHttpHeader($data['code'], get_class($exception)));

		// 判断异常类型
		// 对于CHttpException，也按照error来处理
		if($exception instanceof CHttpException || !YII_DEBUG)
			$this->render('error',$data);
		else
		{
			if($this->isAjaxRequest())
				$app->displayException($exception);
			else
				$this->render('exception',$data);
		}
	}
	// 如果是终端应用（console application），则直接展示异常
	else
		$app->displayException($exception);
}
```

```php
<?php
protected function handleError($event)
{
	$trace=debug_backtrace();
	// skip the first 3 stacks as they do not tell the error position
	if(count($trace)>3)
		$trace=array_slice($trace,3);
	$traceString='';
	foreach($trace as $i=>$t)
	{
		if(!isset($t['file']))
			$trace[$i]['file']='unknown';

		if(!isset($t['line']))
			$trace[$i]['line']=0;

		if(!isset($t['function']))
			$trace[$i]['function']='unknown';

		$traceString.="#$i {$trace[$i]['file']}({$trace[$i]['line']}): ";
		if(isset($t['object']) && is_object($t['object']))
			$traceString.=get_class($t['object']).'->';
		$traceString.="{$trace[$i]['function']}()\n";

		unset($trace[$i]['object']);
	}

	$app=Yii::app();
	// 如果是Web应用
	if($app instanceof CWebApplication)
	{
		// 判断错误类型
		switch($event->code)
		{
			case E_WARNING:
				$type = 'PHP warning';
				break;
			case E_NOTICE:
				$type = 'PHP notice';
				break;
			case E_USER_ERROR:
				$type = 'User error';
				break;
			case E_USER_WARNING:
				$type = 'User warning';
				break;
			case E_USER_NOTICE:
				$type = 'User notice';
				break;
			case E_RECOVERABLE_ERROR:
				$type = 'Recoverable error';
				break;
			default:
				$type = 'PHP error';
		}
		// HTTP响应码为500
		$this->_error=$data=array(
			'code'=>500,
			'type'=>$type,
			'message'=>$event->message,
			'file'=>$event->file,
			'line'=>$event->line,
			'trace'=>$traceString,
			'traces'=>$trace,
		);
		if(!headers_sent())
			header("HTTP/1.0 500 Internal Server Error");
		if($this->isAjaxRequest())
			$app->displayError($event->code,$event->message,$event->file,$event->line);
		elseif(YII_DEBUG)
			// 开了debug，则作为exception来处理
			$this->render('exception',$data);
		else
			$this->render('error',$data);
	}
	else
		$app->displayError($event->code,$event->message,$event->file,$event->line);
}
```

上面的代码最终显示异常/错误信息，是通过方法`render`、以及应用实例的`displayError`和`displayException`方法来完成。

**render**

```php
<?php
protected function render($view,$data)
{
	// 注意这个地方，如果配置了errorAction，则可以指定目标controller的某个action来处理错误
	/*
	 * 配置方式：
	 * 'components' => array(
	 * 		'errorHandler' => array(
     *      	'errorAction'=>'api/index/error',
     *     ),
     *     ...
     */
	if($view==='error' && $this->errorAction!==null)
		Yii::app()->runController($this->errorAction);
	else
	{
		// additional information to be passed to view
		$data['version']=$this->getVersionInfo();
		$data['time']=time();
		$data['admin']=$this->adminInfo;
		
		// 看看下面getViewFile的实现
		include($this->getViewFile($view,$data['code']));
	}
}

protected function getViewFile($view,$code)
{
	$viewPaths=array(
		Yii::app()->getTheme()===null ? null :  Yii::app()->getTheme()->getSystemViewPath(),
		Yii::app() instanceof CWebApplication ? Yii::app()->getSystemViewPath() : null,
		YII_PATH.DIRECTORY_SEPARATOR.'views',
	);

	foreach($viewPaths as $i=>$viewPath)
	{
		if($viewPath!==null)
		{
			 // 看看下面getViewFileInternal的实现
			 $viewFile=$this->getViewFileInternal($viewPath,$view,$code,$i===2?'en_us':null);
			 if(is_file($viewFile))
			 	 return $viewFile;
		}
	}
}

protected function getViewFileInternal($viewPath,$view,$code,$srcLanguage=null)
{
	$app=Yii::app();
	if($view==='error')
	{
		$viewFile=$app->findLocalizedFile($viewPath.DIRECTORY_SEPARATOR."error{$code}.php",$srcLanguage);
		if(!is_file($viewFile))
			$viewFile=$app->findLocalizedFile($viewPath.DIRECTORY_SEPARATOR.'error.php',$srcLanguage);
	}
	else
		$viewFile=$viewPath.DIRECTORY_SEPARATOR."exception.php";
	return $viewFile;
}

```

上面代码的逻辑是 - 对于error类型的信息，Yii会依次在以下目录中寻找名为`error{$code}.php`文件来展示错误/异常信息：

1. WebRoot/themes/ThemeName/views/system
2. WebRoot/protected/views/system
3. yii/framework/views

如果没有找到，则以相同的次序在这些目录中查找`error.php`文件。

对于exception类型信息，则是查找`exception.php`文件。

所以如果应用开发过程需要定制4xx、5xx的错误页面，可以在`WebRoot/protected/views/system`或`WebRoot/themes/ThemeName/views/system`放置对应的错误模板页面。

**displayError**

```php
<?php
public function displayError($code,$message,$file,$line)
{
	if(YII_DEBUG)
	{
		echo "<h1>PHP Error [$code]</h1>\n";
		echo "<p>$message ($file:$line)</p>\n";
		echo '<pre>';

		$trace=debug_backtrace();
		// skip the first 3 stacks as they do not tell the error position
		if(count($trace)>3)
			$trace=array_slice($trace,3);
		foreach($trace as $i=>$t)
		{
			if(!isset($t['file']))
				$t['file']='unknown';
			if(!isset($t['line']))
				$t['line']=0;
			if(!isset($t['function']))
				$t['function']='unknown';
			echo "#$i {$t['file']}({$t['line']}): ";
			if(isset($t['object']) && is_object($t['object']))
				echo get_class($t['object']).'->';
			echo "{$t['function']}()\n";
		}

		echo '</pre>';
	}
	else
	{
		echo "<h1>PHP Error [$code]</h1>\n";
		echo "<p>$message</p>\n";
	}
}
```

**displayException**

```php
<?php
public function displayException($exception)
{
	if(YII_DEBUG)
	{
		echo '<h1>'.get_class($exception)."</h1>\n";
		echo '<p>'.$exception->getMessage().' ('.$exception->getFile().':'.$exception->getLine().')</p>';
		echo '<pre>'.$exception->getTraceAsString().'</pre>';
	}
	else
	{
		echo '<h1>'.get_class($exception)."</h1>\n";
		echo '<p>'.$exception->getMessage().'</p>';
	}
}
```

### 总结

由上述分析可知，基于Yii框架开发应用时，有以下几点注意事项：

- 可以通过配置组件`errorHandler`的`errorAction`属性来定制异常/错误处理过程
- 可以通过在`WebRoot/themes/ThemeName/views/system`或`WebRoot/protected/views/system`放置模板（名为`error{$code}.php`）来定制错误/异常展示方式
- 在有意抛出异常由Yii框架捕获时，需明确异常的类型是否应为`CHttpException`，只有`CHttpException`实例初始化时指定的code才能成为HTTP响应码
- 可以对事件`onError`、`onException`绑定事件处理过程，进行额外的处理，比如记录错误/异常、触发告警等


### 参考资料

- [PHP手册 - 错误处理和日志记录](http://php.net/manual/zh/book.errorfunc.php)
- [Error Handling](http://www.yiiframework.com/doc/guide/1.1/en/topics.error)
- [PHP调试技术手册](/assets/uploads/files/PHP-Debug-Manual-public.pdf)