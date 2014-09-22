Title: 流行PHP项目的phpmetrics分析（译）
Date: 2014-09-22
Author: youngsterxyf
Slug: phpmetrics-of-popular-php-projects
Tags: 翻译, PHP

原文：[phpmetrics of popular php projects](https://peteraba.com/blog/phpmetrics-of-popular-projects/)

译者：[youngsterxyf](https://github.com/youngsterxyf)

之前我偶然发现一个名为[phpmetrics](http://www.phpmetrics.org/)的新工具，可用于计算及展示php的度量指标。我当时立马喜欢上了这个工具，并决定用它分析我认为重要的一些php项目。
我知道这个项目列表还远远不够完善，但应该仍然值得一看。我特别喜欢其中的“可维护性”报告，我发现视觉上那些红色的斑点就和丑陋的代码一样令人厌恶。

这个工具貌似还有点小bug，我会尽力尽快修复这个工具项目的这些小问题。

**一些重要的说明**

- 目前我还无法得到Cakephp和Typo3的分析报告，之后我会尽快调查一下这个问题。
- 我是在完整的代码库或下载的源码包上执行这个工具的，这意味着某些情况下还分析了项目的外部依赖库。之后我可能会调整，但目前不在计划之内。
- 有些项目包含很多代码库，所以我无法确保测试的都市正确的那个代码库。*Joomla*尤其可能这样。
- 某些项目并非非常知名，但在github上呈现关注度上升趋势。
- dm-mailer这个项目无足轻重，只是我最新的个人兴趣项目。我将它与phpmetrics一起归到Backfire一节。
- 注意：php-yaf和phalcon都是非常有意思的php框架，但多数代码是C实现的，因此没有包含进来。

------

说明：阅读该报告的一点小提示：

- 更多的斑点只是意味着更多的类
- 红色意味着不可维护，黄色表示可接受，绿色则表明良好、可维护的代码。

------

### 分析结果

#### 框架

项目：[agavi](http://www.agavi.org/)

可维护性：![agavi-phpmetrics](/assets/uploads/pics/phpmetrics-result/agavi-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/agavi/report.html)

代码库：[戳这里](https://github.com/agavi/agavi)

最近提交（均指master分支上的）：*4个月内*

------

项目：[aura](http://auraphp.com/)

可维护性：![aura-phpmetrics](/assets/uploads/pics/phpmetrics-result/aura-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/aura/report.html)

代码库：[戳这里](https://github.com/auraphp/Aura.Framework_Project)

最近提交：1周内

------

项目：[cakephp](http://cakephp.org/)

可维护性：![cakephp-phpmetrics](/assets/uploads/pics/phpmetrics-result/na.png)

分析报告：<s>戳这里</s>

代码库：[戳这里](https://github.com/cakephp/cakephp)

最近提交：1周内

------

项目：[codeigniter](https://ellislab.com/codeigniter)

可维护性：![codeigniter-phpmetrics](/assets/uploads/pics/phpmetrics-result/codeigniter-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/codeigniter/report.html)

代码库：[戳这里](https://github.com/EllisLab/CodeIgniter)

最近提交：1周内

------

项目：[deano](https://github.com/colindean/deano)

可维护性：![deano-phpmetrics](/assets/uploads/pics/phpmetrics-result/deano-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/deano/report.html)

代码库：[戳这里](https://github.com/colindean/deano)

最近提交：*10个月内*

------

项目：[fatfree](http://fatfreeframework.com/home)

可维护性：![fatfree-phpmetrics](/assets/uploads/pics/phpmetrics-result/fatfree-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/fatfree/report.html)

代码库：[戳这里](https://github.com/bcosca/fatfree)

最近提交：1个月内

------

项目：[flight](http://flightphp.com/)

可维护性：![flight-phpmetrics](/assets/uploads/pics/phpmetrics-result/flight-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/flight/report.html)

代码库：[戳这里](https://github.com/mikecao/flight)

最近提交：2周内

------

项目：[fuelphp](http://fuelphp.com/)

可维护性：![fuelphp-phpmetrics](/assets/uploads/pics/phpmetrics-result/fuelphp-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/fuelphp/report.html)

代码库：[戳这里](https://github.com/fuel/fuel)

最近提交：2个月内

------

项目：[laravel](http://laravel.com/)

可维护性：![laravel-phpmetrics](/assets/uploads/pics/phpmetrics-result/laravel-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/laravel/report.html)

代码库：[戳这里](https://github.com/laravel/laravel)

最近提交：2周内

------

项目：[limonade](http://limonade-php.github.io/)

可维护性：![limonade-phpmetrics](/assets/uploads/pics/phpmetrics-result/limonade-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/limonade/report.html)

代码库：[戳这里](https://github.com/sofadesign/limonade/)

最近提交：2个月内

------

项目：[nette](http://nette.org/en/)

可维护性：![nette-phpmetrics](/assets/uploads/pics/phpmetrics-result/nette-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/nette/report.html)

代码库：[戳这里](https://github.com/nette/nette)

最近提交：1周内

------

项目：[phavour](http://phavour-project.com/)

可维护性：![phavour-phpmetrics](/assets/uploads/pics/phpmetrics-result/phavour-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/phavour/report.html)

代码库：[戳这里](https://github.com/phavour/phavour)

最近提交：*6个月内*

------

项目：[php-mvc(advanced)](http://www.php-mvc.net/)

可维护性：![php-mvc-advanced-phpmetrics](/assets/uploads/pics/phpmetrics-result/php-mvc-advanced-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/php-mvc-advanced/report.html)

代码库：[戳这里](https://github.com/panique/php-mvc-advanced)

最近提交：2周内

------

项目：[phpixie](http://phpixie.com/)

可维护性：![phpixie-phpmetrics](/assets/uploads/pics/phpmetrics-result/phpixie-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/phpixie/report.html)

代码库：[戳这里](https://github.com/dracony/PHPixie)

最近提交：*5个月内*

------

项目：[popphp2](http://www.popphp.org/)

可维护性：![popphp2-phpmetrics](/assets/uploads/pics/phpmetrics-result/popphp2-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/popphp2/report.html)

代码库：[戳这里](https://github.com/popphp/popphp2)

最近提交：3周内

------

项目：[silex](http://silex.sensiolabs.org/)

可维护性：![silex-phpmetrics](/assets/uploads/pics/phpmetrics-result/silex-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/silex/report.html)

代码库：[戳这里](https://github.com/silexphp/Silex)

最近提交：1周内

------

项目：[slim](http://slimframework.com/)

可维护性：![slim-phpmetrics](/assets/uploads/pics/phpmetrics-result/slim-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/slim/report.html)

代码库：[戳这里](https://github.com/codeguy/Slim)

最近提交：5个月内

------

项目：[symfony1](http://symfony.com/legacy)

可维护性：![symfony1-phpmetrics](/assets/uploads/pics/phpmetrics-result/symfony1-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/symfony1/report.html)

代码库：[戳这里](https://github.com/symfony/symfony1)

最近提交：*2年内*

------

项目：[symfony2](http://symfony.com/)

可维护性：![symfony2-phpmetrics](/assets/uploads/pics/phpmetrics-result/symfony2-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/symfony2/report.html)

代码库：[戳这里](https://github.com/symfony/symfony)

最近提交：1周内

------

项目：[typo3](http://typo3.org/)

可维护性：![typo3-phpmetrics](/assets/uploads/pics/phpmetrics-result/na.png)

分析报告：<s>戳这里</s>

代码库：[戳这里](https://git.typo3.org/Packages/TYPO3.CMS.git)

最近提交：1周内

------

项目：[yii1](http://www.yiiframework.com/)

可维护性：![yii1-phpmetrics](/assets/uploads/pics/phpmetrics-result/yii1-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/yii1/report.html)

代码库：[戳这里](https://github.com/yiisoft/yii)

最近提交：2周内

------

项目：[yii2](http://www.yiiframework.com/)

可维护性：![yii2-phpmetrics](/assets/uploads/pics/phpmetrics-result/yii2-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/yii2/report.html)

代码库：[戳这里](https://github.com/yiisoft/yii2)

最近提交：1周内

------

项目：[zf1](http://framework.zend.com/)

可维护性：![zf1-phpmetrics](/assets/uploads/pics/phpmetrics-result/zf1-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/zf1/report.html)

代码库：[戳这里](https://github.com/zendframework/zf1)

最近提交：1周内

------

项目：[zf2](http://framework.zend.com/)

可维护性：![zf2-phpmetrics](/assets/uploads/pics/phpmetrics-result/zf2-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/zf2/report.html)

代码库：[戳这里](https://github.com/zendframework/zf2)

最近提交：2周内

------

#### CMS

项目：[drupal](https://www.drupal.org/)

可维护性：![drupal-phpmetrics](/assets/uploads/pics/phpmetrics-result/drupal-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/drupal/report.html)

代码库：[戳这里](https://github.com/drupal/drupal)

最近提交：1周内

------

项目：[joomla](http://www.joomla.org/)

可维护性：![joomla-phpmetrics](/assets/uploads/pics/phpmetrics-result/joomla-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/joomla/report.html)

代码库：[戳这里](https://github.com/joomla/joomla-framework)

最近提交：5个月内

------

项目：[grav](http://getgrav.org/)

可维护性：![grav-phpmetrics](/assets/uploads/pics/phpmetrics-result/grav-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/grav/report.html)

代码库：[戳这里](https://github.com/getgrav/grav)

最近提交：1周内

------

项目：[pagekit](http://pagekit.com/)

可维护性：![pagekit-phpmetrics](/assets/uploads/pics/phpmetrics-result/pagekit-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/pagekit/report.html)

代码库：[戳这里](https://github.com/pagekit/pagekit)

最近提交：1周内

------

项目：[os webasyst projects](http://www.webasyst.com/)

可维护性：![os-webasyst-projects-phpmetrics](/assets/uploads/pics/phpmetrics-result/os-webasyst-projects-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/webasyst/report.html)

代码库：N/A

最近提交：N/A

------

项目：[wordpress](http://wordpress.org/)

可维护性：![wordpress-phpmetrics](/assets/uploads/pics/phpmetrics-result/wordpress-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/wordpress/report.html)

代码库：[戳这里](https://github.com/WordPress/WordPress)

最近提交：1周内

------

#### 电子商务

项目：[magento1(1.8 copy)](http://magento.com/)

可维护性：![magento1-phpmetrics](/assets/uploads/pics/phpmetrics-result/magento1-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/magento1/report.html)

代码库：[戳这里](https://bitbucket.org/ecgkodokux/magento1.8.git)

最近提交：N/A

------

项目：[magento2](http://magento.com/)

可维护性：![magento2-phpmetrics](/assets/uploads/pics/phpmetrics-result/magento2-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/magento2/report.html)

代码库：[戳这里](https://github.com/magento/magento2)

最近提交：1周内

------

项目：[opencart](http://www.opencart.com/)

可维护性：![opencart-phpmetrics](/assets/uploads/pics/phpmetrics-result/opencart-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/opencart/report.html)

代码库：[戳这里](https://github.com/opencart/opencart)

最近提交：1周内

------

项目：[oscommerce](http://www.oscommerce.com/)

可维护性：![oscommerce-phpmetrics](/assets/uploads/pics/phpmetrics-result/oscommerce-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/oscommerce/report.html)

代码库：[戳这里](https://github.com/osCommerce/oscommerce)

最近提交：2年内

------

项目：[prestashop](http://www.prestashop.com/)

可维护性：![prestashop-phpmetrics](/assets/uploads/pics/phpmetrics-result/prestashop-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/prestashop/report.html)

代码库：[戳这里](https://github.com/PrestaShop/PrestaShop)

最近提交：1周内

------

项目：[sylius](http://sylius.org/)

可维护性：![sylius-phpmetrics](/assets/uploads/pics/phpmetrics-result/sylius-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/sylius/report.html)

代码库：[戳这里](https://github.com/Sylius/Sylius)

最近提交：*10个月内*

------

项目：[virtuemart](http://virtuemart.net/)

可维护性：![virtuemart-phpmetrics](/assets/uploads/pics/phpmetrics-result/virtuemart-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/virtuemart/report.html)

代码库：[戳这里](http://dev.virtuemart.net/projects/virtuemart/repository)

最近提交：N/A

------

项目：[zencart](http://www.zen-cart.com/)

可维护性：![zencart-phpmetrics](/assets/uploads/pics/phpmetrics-result/zencart-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/zencart/report.html)

代码库：[戳这里](https://github.com/zencart/zc-v1-series)

最近提交：1周内

------

#### 开发工具

项目：[codeception](http://codeception.com/)

可维护性：![codeception-phpmetrics](/assets/uploads/pics/phpmetrics-result/codeception-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/codeception/report.html)

代码库：[戳这里](https://github.com/Codeception/Codeception)

最近提交：1周内

------

项目：[phpunit](http://phpunit.de/)

可维护性：![phpunit-phpmetrics](/assets/uploads/pics/phpmetrics-result/phpunit-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/phpunit/report.html)

代码库：[戳这里](https://github.com/sebastianbergmann/phpunit)

最近提交：1周内

------

#### 其他

项目：[piwik](http://piwik.org/)

可维护性：![piwik-phpmetrics](/assets/uploads/pics/phpmetrics-result/piwik-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/piwik/report.html)

代码库：[戳这里](https://github.com/piwik/piwik)

最近提交：1周内

------

#### Backfire

项目：[dm-mailer](https://github.com/peteraba/zf2-mailer)

可维护性：![dm-mailer-phpmetrics](/assets/uploads/pics/phpmetrics-result/dm-mailer-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/dm-mailer/report.html)

代码库：[戳这里](https://github.com/peteraba/zf2-mailer)

最近提交：*7个月内*

------

项目：[phpmetrics](http://www.phpmetrics.org/)

可维护性：![phpmetrics-phpmetrics](/assets/uploads/pics/phpmetrics-result/phpmetrics-phpmetric-maintenability.png)

分析报告：[戳这里](https://peteraba.com/metrics/phpmetrics/phpmetrics/report.html)

代码库：[戳这里](https://github.com/Halleck45/PhpMetrics)

最近提交：1周内

------

#### 问题(Issues)

**Cakephp**

    :::text
    594/666 [========================>---]  89%

    [Exception]                         
    Closure detected instead of method


**Deano**

    :::text
    2/9 [======>---------------------]  22%file /home/peter/dev/php/opensource/deano/views/layout/layout.php is not valid and has been skipped
    9/9 [============================] 100%file /home/peter/dev/php/opensource/deano/deano.php is not valid and has been skipped


**Limonade**

    :::text
     9/16 [===============>------------]  56%file /home/peter/dev/php/opensource/limonade/examples/example02/index.php is not valid and has been skipped
    16/16 [============================] 100%file /home/peter/dev/php/opensource/limonade/examples/example06/index.php is not valid and has been skipped


**Magento**

    :::text
    3361/9868 [=========>------------------]  34%file ../../opensource/magento2/lib/internal/Zend/Mail/Protocol/Pop3.php is not valid and has been skipped


**Pagekit**

    :::text
    102/215 [=============>--------------]  47%file /home/peter/dev/php/opensource/pagekit/extensions/system/src/System/Console/skeleton/extension/src/Controller/SiteController.php is not valid and has been skipped
    103/215 [=============>--------------]  47%file /home/peter/dev/php/opensource/pagekit/extensions/system/src/System/Console/skeleton/extension/src/DefaultExtension.php is not valid and has been skipped
    105/215 [=============>--------------]  48%file /home/peter/dev/php/opensource/pagekit/extensions/system/src/System/Console/skeleton/theme/src/DefaultTheme.php is not valid and has been skipped


**Symfony1**

    :::text
    199/1320 [====>-----------------------]  15%file /home/peter/dev/php/opensource/symfony1/lib/task/generator/skeleton/module/module/actions/actions.class.php is not valid and has been skipped
    205/1320 [====>-----------------------]  15%file /home/peter/dev/php/opensource/symfony1/lib/task/generator/skeleton/app/web/index.php is not valid and has been skipped
    206/1320 [====>-----------------------]  15%file /home/peter/dev/php/opensource/symfony1/lib/task/generator/skeleton/app/app/config/ApplicationConfiguration.class.php is not valid and has been skipped
    397/1320 [========>-------------------]  30%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfPropelPlugin/data/generator/sfPropelModule/admin/skeleton/lib/helper.php is not valid and has been skipped
    398/1320 [========>-------------------]  30%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfPropelPlugin/data/generator/sfPropelModule/admin/skeleton/lib/configuration.php is not valid and has been skipped
    399/1320 [========>-------------------]  30%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfPropelPlugin/data/generator/sfPropelModule/admin/skeleton/actions/actions.class.php is not valid and has been skipped
    445/1320 [=========>------------------]  33%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfPropelPlugin/data/generator/sfPropelModule/default/skeleton/actions/actions.class.php is not valid and has been skipped
    652/1320 [=============>--------------]  49%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfDoctrinePlugin/data/generator/sfDoctrineModule/admin/skeleton/lib/helper.php is not valid and has been skipped
    653/1320 [=============>--------------]  49%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfDoctrinePlugin/data/generator/sfDoctrineModule/admin/skeleton/lib/configuration.php is not valid and has been skipped
    654/1320 [=============>--------------]  49%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfDoctrinePlugin/data/generator/sfDoctrineModule/admin/skeleton/actions/actions.class.php is not valid and has been skipped
    700/1320 [==============>-------------]  53%file /home/peter/dev/php/opensource/symfony1/lib/plugins/sfDoctrinePlugin/data/generator/sfDoctrineModule/default/skeleton/actions/actions.class.php is not valid and has been skipped


**Typo3**

    :::text
    76/2583 [>---------------------------]   2%

    [Exception]                         
    Closure detected instead of method 
