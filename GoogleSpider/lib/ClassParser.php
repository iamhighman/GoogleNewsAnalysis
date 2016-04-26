<?php 
                                                                          
class Parser{

   function find2find($str, $start, $end){
      $tmp = explode($start, $str);
      if(count($tmp)<2) return "";
      $tmp = explode($end, $tmp[1]);
      return $tmp[0];
   }
   
   function microtime_float(){
      list($usec, $sec) = explode(" ", microtime());
      return ((float)$usec + (float)$sec);
   }

   function getDirectory($token, $type){
      $base = "/home/Work2T/UPitts/GoogleNews/data/".$type."/";
      $tmp = MD5($token);
      return $base.substr($tmp, 0, 1)."/".$token.".html";
   }

   function saveContent($file, $result){
      $idx = $file;
      $handle = @fopen($idx, "w");
      fwrite($handle, $result);
      fclose($handle);
   }

   function fetchWeb($link){ 
      if(rand(0,1) > 0.5){
         echo "P1:";
         $proxy_server = "114.34.176.139:3128";
      }else{
         echo "P2:";
         $proxy_server = "114.32.92.135:3128";
      }
      $proxy_server = "114.32.92.135:3128";
      $user_agent = "Mozilla/5.0 (compatible; MSIE 6.01; Windows NT 6.0)";
      
      $resource = curl_init();
      curl_setopt($resource, CURLOPT_URL, $link);
      curl_setopt($resource, CURLOPT_USERAGENT, $user_agent);
      curl_setopt($resource, CURLOPT_FOLLOWLOCATION, 1);
      curl_setopt($resource, CURLOPT_RETURNTRANSFER, 1);
      curl_setopt($resource, CURLOPT_AUTOREFERER, true);
      curl_setopt($resource, CURLOPT_TIMEOUT, 5);
      curl_setopt($resource, CURLOPT_PROXY, "$proxy_server");
      $input =  curl_exec($resource);
      curl_close($resource);
      return $input;
   }

   function fetchWebNoProxy($link){
      $user_agent = "Mozilla/5.0 (compatible; MSIE 5.01; Windows NT 5.0)";

      $resource = curl_init();
      curl_setopt($resource, CURLOPT_URL, $link);
      curl_setopt($resource, CURLOPT_USERAGENT, $user_agent);
      curl_setopt($resource, CURLOPT_FOLLOWLOCATION, 1);
      curl_setopt($resource, CURLOPT_RETURNTRANSFER, 1);
      curl_setopt($resource, CURLOPT_REFERER,"http://www.google.com");
      curl_setopt($resource, CURLOPT_TIMEOUT, 5);
      $input =  curl_exec($resource);
      curl_close($resource);
      return $input;
   }

   function postWeb($url, $post){
      $resource = curl_init();
      //$proxy = "192.168.0.125:3128";
      //curl_setopt($resource, CURLOPT_PROXY, "$proxy");
      curl_setopt($resource, CURLOPT_TIMEOUT,10); 
      curl_setopt($resource, CURLOPT_URL, $url);
      curl_setopt($resource, CURLOPT_POST, 1);
      curl_setopt($resource, CURLOPT_POSTFIELDS, "$post");
      curl_setopt($resource, CURLOPT_FOLLOWLOCATION, 1);
      curl_setopt($resource, CURLOPT_RETURNTRANSFER, 1);
      $content = curl_exec($resource);      
      curl_close($resource);
      return $content;
   }

   function DetectCharset($s){ //偵測string的編碼
      $ary[] = "BIG-5";
      $ary[] = "EUC-CN";
      $ary[] = "CP936";
      $ary[] = "UTF-8";
      $ary[] = "ISO-2022-JP";
      $ary[] = "EUC-JP";
             
      return  mb_detect_encoding($s, $ary);
   }

   function toCharsetUTF8($str){   //將string轉成utf8
//      $encoding =  $this->DetectCharset($str);
      $encoding = mb_detect_encoding($str, "auto");
      echo $encoding; $encoding = "euc-kr";
      if ($encoding == false || $encoding == 'UTF-8' || $encoding == 'ASCII'){  
          return $str;  
      }else{  
          return mb_convert_encoding($str, 'UTF-8', $encoding);
      }
   }  

} 
?>
