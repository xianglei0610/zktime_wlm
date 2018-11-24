/*
File name: electro_map.js
Description: electro-map of ZKAccess5.0 Security System
Author: Darcy
Create date: 2010.10.26
Company: ZKTeco
*/
    var tabs_width = 0;//tabs宽度（地图宽度)

    //浏览器窗口变化时，整个tabs自适应--start
    $(window).resize(function() {
        tabs_width = $(".tabs").width()
        $(".map").each(function(){
            //resize_image($(this));
        });
    });
    //图片不变形
//    function resize_image(obj)
//    {
//        var obj_width = obj.width;
//        var obj_height = obj.height;
//        if(obj_width > tabs_width)
//        {
//            $(obj).css("width", (tabs_width - 20) + "px");
//            $(obj).css("height", obj_height * ((tabs_width - 20) / obj_width) + "px");
//
//        }
//    } 
    //浏览器窗口变化时，整个tabs自适应--end
    
    //对门循环处理top和left时的公共代码
    var new_door_top = 0;
    var new_door_left = 0;
    var new_door_width = 0; 
    function loop_doors($img, scale)
    {
        var door_width = parseFloat($img.css("width").replace("px", ""), 10);//parseFloat否则会出现16.5/2=8
        new_door_width = parseFloat(door_width) * scale;//门宽度按比例变化
        var door_top = parseFloat($img.css("top").replace("px", ""), 10);//门的上边距
        var door_left = parseFloat($img.css("left").replace("px", ""), 10);//当前门的左边距
        //alert('door_left='+door_left+'door_top='+door_top+' scale='+scale+"  door_width="+door_width)
        //中点(door_top+door_width/2, door_left + door_width/2)按比例变化即可
        //alert(new_door_width)
        new_door_top = (door_top + door_width/2) * scale - new_door_width/2;
        new_door_left = (door_left + door_width/2) * scale - new_door_width/2;
    }

    //实现地图的放大缩小--start
    function zoom_img($img, scale, left, top)
    {
        var img_width = $img.width();//当前地图宽度。不带px
        var img_height = $img.height();
        var img_top = $img.offset().top;
        var img_left = $img.offset().left;
        //alert('top--='+img_top+" left="+img_left);
        var box_width = scale * img_width;//放大或缩小后的地图宽度
        var box_height = scale * img_height;
        var valid = true;//标记能够继续缩小
        //比较imgBox的长宽比与img的长宽比大小
        
        //检测地图的宽度是否达到上限1120px
        //alert(box_width)
        //含新增的图片已经超过1120和放大后达到1120
        if(scale > 1 && (img_width > 1120 || box_width > 1120))//方法时无论原宽度还是放大之后的宽度均不能大于1120
        {
            alert(gettext("地图宽度到达上限(1120px)，不能再放大！"));
            return false;
        }
        else if(scale < 1 && (img_width < 500 || box_width < 400))//缩小时，注释同上
        {
            alert(gettext("地图宽度到达下限(400px)，不能再缩小！"));
            return false;
        }
        
        if(scale < 1 && (img_height < 100 || box_height < 100))//缩小时，注释同上
        {
            alert(gettext("地图高度到达下限(100px)，不能再缩小！"));
            return false;
        }
    
        //门图标联动--坐标和大小
        var $zoom_imgs = $img.parent().find(".can_drag");//取到当前地图上的门


        //要先检测所有的门的坐标是否有效，只要有一个无效，将无法继续，直接返回，不做缩小操作（扩大不受影响）
        $zoom_imgs.each(function(){
            loop_doors($(this), scale);
            
            if(scale < 1)
            {
                if(new_door_top < 50 || new_door_left < 50)
                {
                    valid = false;
                    //return false;
                }
            }

            if(!valid)
            {
                return false;//中断each
            }
        });

        if(!valid)
        {
            alert(gettext("门图标的位置（Top或Left）到达下限，请稍作调整后再进行缩小操作！"));
            return false;
        }
        
        $zoom_imgs.each(function(){
            loop_doors($(this), scale);
            //alert('new_door_left='+new_door_left+'new_door_top='+new_door_top)
            $(this).css("top", new_door_top);//上边距
            $(this).css("left", new_door_left);//左边距
            $(this).css("width", new_door_width);//只控制width即可，height：auto，默认40px
        });
        //重新设置img的width和height
        $img.width(box_width);
        $img.height(box_height);
    }
    
    $("#id_smaller").click(function(){
        var $zoom_img = $("#"+$(".current").attr("href").split("#")[1]+" img:last");//取到当前地图图片
        zoom_img($zoom_img, 0.8, 0, 0);
    });

    $("#id_bigger").click(function(){
        var $zoom_img = $("#"+$(".current").attr("href").split("#")[1]+" img:last");
        zoom_img($zoom_img, 1.25, 0, 0);
    });
    //实现地图的放大缩小--end
    
    

    
    


