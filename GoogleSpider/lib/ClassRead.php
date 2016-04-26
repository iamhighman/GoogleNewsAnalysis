<?php
require_once './Readability.php';

class Read{

   var $readability = new Readability($html, $url);

   function getMainText($html){

      $this->readability->debug = false;
      $this->readability->convertLinksToFootnotes = true;
      $result = $this->readability->init();
      
      if ($result) {
         $title = $readability->getTitle()->textContent, "\n\n";
         $body = $content = $readability->getContent()->innerHTML;
         return $body;
      } else {
         echo 'Looks like we couldn\'t find the content. :(';
      }

}

