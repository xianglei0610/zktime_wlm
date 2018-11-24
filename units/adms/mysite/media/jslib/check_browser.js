   //显示、影藏列表thead右侧补齐的monitor_hdiv_right
   function check_brower_version(has_data)
   { 
       if($.browser.msie)  
       {
           var ver=$.browser.version;
           if(ver == 6.0)
           {
               if(has_data == true)
               {
                   $(".monitor_hdiv_right").show();
               }
               else
               {
                   $(".monitor_hdiv_right").hide();
               }
           }
           else if(ver == 7.0)
           {
               $(".monitor_hdiv_right").hide();
           }
           else if(ver == 8.0)
           {
               $(".monitor_hdiv_right").hide();
           }
       }
       else
       {
           $(".monitor_hdiv_right").show();
       }
   }    
