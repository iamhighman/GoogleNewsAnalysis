<?php

class CKIP{
   
   function toCharsetBig5($str, $encoding){   //將string轉成big5
     if ($encoding == 'EUC-CN') $encoding = 'CP936';  
     if ($encoding == 'BIG-5' || $encoding == 'ASCII')  
         return $str;  
     else  
         return mb_convert_encoding($str, 'BIG-5', $encoding);
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

   function goCKIP($text){
   	 
   	 if(strlen($text) < 1) return NULL;
   	 
      $sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
         
      // Connect to destination address
      socket_connect($sock, '172.16.155.129', 1501);
         	
   	 $p = xml_parser_create();

      $strSlice = ereg_replace("[<>]&", "", $text);
      $strSlice = ereg_replace("&", "", $strSlice);
      $strSlice = preg_replace("/\s/","",$strSlice);
      $strSlice = $this->toCharsetBig5($strSlice, "UTF-8");  
      
      $request = "<?xml version=\"1.0\" ?>" .
                 "<wordsegmentation version=\"0.1\">" .
                 "<option showcategory=\"1\" />" .
                 "<authentication username=\"highman\" password=\"linux\" />" .
                 "<text>$strSlice</text>" .
                 "</wordsegmentation>";
      
      socket_write($sock,  $request);
      
      usleep(6000000);
      
      $read = @socket_read($sock, 80000);

      xml_parse_into_struct($p, $read, $vals, $index);
      xml_parser_free($p);

      // Close
      socket_close($sock);
            
     $result="";

     foreach($vals as $element){//只處理斷詞結果 過濾掉系統處理狀態
          if($element['level'] == 3){
             $result .= $element['value'];
          }
     }
     
     return $result;
   }   

}

?>
