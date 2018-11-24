$(function(){
    $("#btnUpload").click(function(){
        if($("#txtfilename").val()=='')
        {
            alert("choice a file to upload!");
            return;
        }
        var hl=$("[name='headerln']").val();
        if(!CheckNumber(hl))
        {
            alert("header line No. must be a number!");
            $("[name='headerln']").focus();
            return ;
        };
        var rl=$("[name='recordln']").val();
        if(!CheckNumber(rl))
        {
            alert("record line No. must be a number!");
            $("[name='recordln']").focus();
            return ;
        };
        var rbtf=""
        $("[name='filetype']").each(function(){
                if($(this).attr("checked"))
                {
                    rbtf=$(this);
                }
        });
        var ft=$(rbtf).val()
        var fnft=$("#txtfilename").val();
        fnft=fnft.substr(fnft.lastIndexOf(".")+1);
        if(ft=='xls' && fnft!='xls')
        {
           alert("choice xls file to upload!");
            return;
        }
        else
        {
            if( ft=='txt' && fnft!='txt' && fnft!='csv')
            {
                alert("choice txt or csv  file to upload!");
                return;
                
            };
        };
        var opt={
            url:"/data/import/get_import",
            type:"POST",
            //dataType:"json",
            error:function(XMLHttpRequest, textStatus, errorThrown){
                        alert(textStatus);  
                    },
            success:function(data){
                    //jqery ajax提交文件后，再次获取服务器json信息时，会返回错误，
                    //会在json数据前加上"<pre></pre>"标签，因此需要过漏此标签
                if(data.indexOf('<pre>') != -1) {
                    data = data.substring(5, data.length-6);
                  }
                eval("data=" + data); 
                    
                $("[name='txttablename']").attr("value",data.tablename);
                $("[name='txtfilename']").attr("value",data.filename);
                $("[name='txtfiletype']").attr("value",data.filetype);
                
                $("[name='sparatorvalue']").attr("value",data.sparatorvalue);
                $("[name='headln']").attr("value",data.headln);
                $("[name='recordln']").attr("value",data.recordln);
                
                $("[name='unicode']").attr("value",data.unicode);
                
                //标头checkbox
                var htmlchk="<tr height=20><td width=80></td>"
                var header="<tr height=20><td width=80>"+gettext("文件标头")+"</td>"
                var record="<tr height=20><td width=80></td>"
                var cmbfields="<tr height=20><td width=80>"+gettext("表字段")+"</td>";
                for( i=0;i<data.recorddata.length;i++)
                {
                    htmlchk+="<td><input type='checkbox' name='_chk_"+ i +"' class='fieldschk' checked='checked' /></td>";
                    if (data.headdata.length>0)
                    {   
                        header+="<td width=80>"+data.headdata[i]+"</td>";
                    }
                    else
                    {
                           header+="<td></td>";
                    };
                    record+="<td>"+data.recorddata[i]+"</td>";
                    cmbfields+="<td><select name='_select_"+ i +"'>";
                    
                    for( fld=0;fld< data.fields.length;fld++)
                    {
                        if(fld==i)
                        {
                            cmbfields+="<option value='"+data.fields[fld]+"' selected>"+data.fieldsdesc[fld]+"</option>";
                        }
                        else
                        {
                            cmbfields+="<option value='"+data.fields[fld]+"'>"+data.fieldsdesc[fld]+"</option>";
                        };

                    };
                    cmbfields+="</select></td>";
                };
                htmlchk+="</tr>"
                header+="</tr>"
                record+="</tr>"
                cmbfields+="</tr>"
                $($(".bc")[0]).empty();
                $($(".bc")[0]).append(htmlchk);
                $($(".bc")[0]).append(header);
                $($(".bc")[0]).append(record);
                $($(".bc")[0]).append(cmbfields);
                $("#tddatalist").attr("visibility","visible")
                $("#divdatalist").attr("visibility","visible")
              }
            }
        $("form[name='txtfileform']").ajaxSubmit(opt);
            
    });
    $("#txtfilename").change(function(){
      
      var fnft=$("#txtfilename").val();
      fnft=fnft.substr(fnft.lastIndexOf(".")+1);
      $("[name='filetype']").each(function(){
              if(fnft=='csv' && $(this).val()=='txt')
                {
                    $(this).attr("checked",true);
                };
              if($(this).val()==fnft)
              {
                  $(this).attr("checked",true);
              };
      });
       

    });
    $("#btnImport").click(function(){
        var opt={
            url:"/data/import/file_import",
            type:"POST",
            success:function(data){
                alert(data);
                },
        };
        $("#fileimport").ajaxSubmit(opt);
        
    });
    $("#btnExport").click(function(){
       /* var opt={
            type:"POST",
            url:"/data/export/file_export",
            success:function(msg){
               // alert(msg);
            },
        };
        
        $("#formExport").ajaxSubmit(opt);
        */
        //$("#formExport").Submit();
    });
});

