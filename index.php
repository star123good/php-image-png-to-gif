<?php
    require_once 'vendor/autoload.php';

    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    function create_gif($text_file_name) {
        $i = 0;
        $save_path = realpath("./png");
        $GIF = new Imagick();
        $GIF->setFormat("gif");

        $fh = fopen($text_file_name, 'r');
        while ($line = fgets($fh)) {
            if ($i == 0) {
                $i++; 
                continue;
            }
            $image_data = explode(',', $line);
            $frame = new Imagick();
            $frame->readImage(realpath("./png/". $image_data[1]));
            $frame->setImageDelay($image_data[2]);
            $GIF->addImage($frame);
            $GIF->setImageDispose(2);
        }

        $GIF->writeImages($save_path."/"."animation.gif", true);

        // $factory = new \ImageOptimizer\OptimizerFactory();
        // $optimizer = $factory->get('gif');
        // $filepath = $save_path."/"."animation.gif";

        // $optimizer->optimize($filepath);
        
        header("Content-Type: image/gif");
        echo $GIF->getImagesBlob();
    }

    create_gif("schedule.txt");
?>