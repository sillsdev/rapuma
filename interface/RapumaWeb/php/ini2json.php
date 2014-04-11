<?php

// Convert config (ini-style files) to JSON

    $file = "/usr/share/scriptureforge/rapuma/publishing/ENG/ENG-LATN-JAS/Config/project.conf";
    $script = "python /home/dennis/Projects/rapuma/interface/RapumaWeb/py/config2json.py ";


    // Call the main script
    echo exec($script . $file);

?>

