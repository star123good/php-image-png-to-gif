<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInitcd80ae338d9035896d7db23042d84b62
{
    public static $files = array (
        'a4a119a56e50fbb293281d9a48007e0e' => __DIR__ . '/..' . '/symfony/polyfill-php80/bootstrap.php',
        '6e3fae29631ef280660b3cdad06f25a8' => __DIR__ . '/..' . '/symfony/deprecation-contracts/function.php',
    );

    public static $prefixLengthsPsr4 = array (
        'S' => 
        array (
            'Symfony\\Polyfill\\Php80\\' => 23,
            'Symfony\\Component\\Process\\' => 26,
            'Symfony\\Component\\OptionsResolver\\' => 34,
        ),
        'P' => 
        array (
            'Psr\\Log\\' => 8,
        ),
    );

    public static $prefixDirsPsr4 = array (
        'Symfony\\Polyfill\\Php80\\' => 
        array (
            0 => __DIR__ . '/..' . '/symfony/polyfill-php80',
        ),
        'Symfony\\Component\\Process\\' => 
        array (
            0 => __DIR__ . '/..' . '/symfony/process',
        ),
        'Symfony\\Component\\OptionsResolver\\' => 
        array (
            0 => __DIR__ . '/..' . '/symfony/options-resolver',
        ),
        'Psr\\Log\\' => 
        array (
            0 => __DIR__ . '/..' . '/psr/log/Psr/Log',
        ),
    );

    public static $prefixesPsr0 = array (
        'I' => 
        array (
            'ImageOptimizer' => 
            array (
                0 => __DIR__ . '/..' . '/ps/image-optimizer/src',
            ),
        ),
    );

    public static $classMap = array (
        'Stringable' => __DIR__ . '/..' . '/symfony/polyfill-php80/Resources/stubs/Stringable.php',
        'ValueError' => __DIR__ . '/..' . '/symfony/polyfill-php80/Resources/stubs/ValueError.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixLengthsPsr4 = ComposerStaticInitcd80ae338d9035896d7db23042d84b62::$prefixLengthsPsr4;
            $loader->prefixDirsPsr4 = ComposerStaticInitcd80ae338d9035896d7db23042d84b62::$prefixDirsPsr4;
            $loader->prefixesPsr0 = ComposerStaticInitcd80ae338d9035896d7db23042d84b62::$prefixesPsr0;
            $loader->classMap = ComposerStaticInitcd80ae338d9035896d7db23042d84b62::$classMap;

        }, null, ClassLoader::class);
    }
}
