// -*- coding: utf-8 -*-
___f=function(){
jQuery.validator.messages.required="Requerido"
jQuery.validator.messages.email="No es una dirección de correo electrónico"
jQuery.validator.messages.date="Por favor, introduzca una fecha válida: yyyy/mm/dd."
jQuery.validator.messages.dateISO="Por favor, introduzca una válida (ISO) fecha: yyyy-mm-dd."
jQuery.validator.messages.wZBaseDateField="Por favor, introduzca una fecha válida: yyyy-mm-dd."
jQuery.validator.messages.wZBaseDateTimeField="Por favor, introduzca una fecha válida: yyyy-mm-dd hh:mm:ss."
jQuery.validator.messages.wZBaseTimeField="Por favor, tiempo de entrada válido: hh:mm:ss."
jQuery.validator.messages.wZBaseIntegerField="Por favor, introduzca un número entero."
jQuery.validator.messages.number="Por favor, introduzca un valor válido."
jQuery.validator.messages.digits="Sólo numérico permite"
jQuery.validator.messages.equalTo="Diferentes"
jQuery.validator.messages.minlength=$.validator.format("al menos {0} caracteres (s)")
jQuery.validator.messages.maxlength=$.validator.format("en la mayoría de {0} caracteres (s)")
jQuery.validator.messages.rangelength=$.validator.format("entre {0} y {1} caracteres")
jQuery.validator.messages.range=$.validator.format("Entre {0} y {1} CARACTERES")
jQuery.validator.messages.max=$.validator.format("Entre {0} y {1} CARACTERES")
jQuery.validator.messages.min=$.validator.format("Por favor, introduzca un valor no menor que {0}.")
jQuery.validator.messages.xPIN="sólo numéricos o carta permitido"
jQuery.validator.messages.xNum="sólo numérico permite"
jQuery.validator.messages.xMobile="Número incorrecto del teléfono móvil"
jQuery.validator.messages.xTele="Mal de línea fija número de teléfono"
jQuery.validator.messages.xSQL="No se puede entrar en \" o \'."
}

___f();

if(typeof(catalog)=="undefined") {catalog={}}

catalog["请选择一个字段"] = "  Por favor, seleccione un presentadas.";
catalog["'满足任意一个' 值域必须是以','隔开的多个结果"] = "Sólo los resultados de múltiples divididas con ',' puede cumplir cualquier rango de valores.";
catalog["输入的值错误"] = "valor de la entrada incorrecta";

catalog["确定注销系统?"] = "?Estás seguro para salir del sistema?";
catalog["通讯失败"] = "fracaso";
catalog["确定"] = "Confirmar";
catalog["服务器处理数据失败，请重试！错误码：-616"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo Código de error: -616.";

catalog["日志"] = "Registros";


catalog["请选择一条历史备份记录!"] = "Por favor, seleccione una entrada de copia de seguridad de la historia.";
catalog["还原成功!"] = "Restaurado con éxito";

catalog["间隔时间不能超过一年"] = "Intervalo no puede exceder de un a?o.";
catalog["间隔时间不能小于24小时"] = "Intervalo no puede ser inferior a 24 horas.";
catalog["在当前时间的一个小时内只能备份一次"] = "Copia de seguridad sólo se puede hacer una vez dentro de una hora de tiempo actual!  ";
catalog["请先在服务控制台中设置数据库备份路径"] = "Por favor, establecer la ruta de copia de seguridad de base de datos en la primera consola de servicio";

catalog["全部"] = "Todos los";

catalog["数据格式必须是json格式!"] = "Los datos deben estar en formato JSON.";

catalog["请选择人员!"] = "Por favor, seleccione a una persona!";
catalog["考勤"] = "Asistencia";

catalog["设备名称不能为空"] = "El nombre del dispositivo no puede estar vacío.";
catalog["设备序列号不能为空"] = "El número de serie del dispositivo no puede estar vacío.";
catalog["通讯密码必须为数字"] = "La contrase?a de comunicación debe ser un valor numérico.";
catalog["请输入一个有效的IPv4地址"] = "Por favor, introduzca una dirección IPv4 válida.";
catalog["请输入一个有效的IP端口号"] = "Por favor, introduzca un número válido de IP del puerto.";
catalog["请输入一个RS485地址"] = "Por favor, introduzca una dirección de RS485.";
catalog["RS485地址必须为1到63之间的数字"] = "Una dirección RS485 debe ser un valor numérico entre 1 y 63.";
catalog["请选择串口号"] = "Por favor, seleccione un número de puerto serie.";
catalog["请选择波特率"] = "Por favor, seleccione una velocidad de transmisión.";
catalog["请选择设备所属区域"] = "Por favor, seleccionar un área para el dispositivo.";
catalog["串口：COM"] = "Puerto serie COM";
catalog[" 的RS485地址："] = " S RS485 la dirección";
catalog[" 已被占用！"] = " ha sido ocupada!";
catalog["后台通讯忙，请稍后重试！"] = "la comunicación de fondo está ocupado, por favor, inténtelo de nuevo más tarde!";
catalog["提示：设备连接成功，但获取设备扩展参数失败，继续添加？"] = "Sugerencia: The device is connected successfully, but failed to get the extended parameters for device, Continue to add?";
catalog["提示：设备连接成功，但控制器类型与实际不符，将修改为"] = "Sugerencia: El dispositivo está conectado correctamente, pero el tipo de panel de control de acceso diferente de la real, modificarlo para";
catalog["门控制器，继续添加？"] = "puerta (s) del panel de control. Continuar para agregar?";
catalog["提示：设备连接成功，确定后将添加设备！"] = "Sugerencia: El dispositivo está conectado correctamente, y los tipos de concordancia de los paneles de control de acceso. A?adir el dispositivo después de la confirmación!";
catalog["提示：设备连接失败（错误码："] = "Sugerencia: El dispositivo no se conecta (código de error:";
catalog["），确定添加该设备？"] = "). ?Estás seguro de agregar este dispositivo?";
catalog["提示：设备连接失败（原因："] = "Sugerencia: El dispositivo no se conecta (causa:";
catalog["服务器处理数据失败，请重试！错误码：-615"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo Código de error: -615.";
catalog["提示：新增设备将清空设备中的所有数据，确定要继续？"] = "Sugerencia: Agregar el dispositivo se borrarán todos los datos en el dispositivo, asegúrese de continuar?";
catalog["编辑设备信息("] = "editar la información del dispositivo";
catalog["对不起，您没有访问该页面的权限，不能浏览更多信息！"] = "Lo sentimos, usted no tiene derecho a visitar esta página, por lo que no puede ver más información!";

catalog["是否中止数据下载，并清除命令队列?"] = "?Quieres dejar de descarga de datos y las colas de mando claras?";
catalog["清除缓存命令成功!"] = "Los comandos de caché se borran con éxito!";
catalog["清除缓存命令失败!"] = "Los comandos de caché no se eliminan con éxito!";

catalog["员工排班表"] = "Personal tabla de programación";
catalog["临时排班表"] = "Temporal tabla de programación";
catalog["排班时间段详细明细"] = "Secuencia de cambios detalles Calendario";
catalog["排班时间段详细明细(仅显示三个月)"] = "turnos de detalles el calendario (sólo tres meses)";
catalog["排班时间段详细明细(仅显示到年底)"] = "turnos de detalles el calendario (sólo el final del ejercicio";

catalog["请选择时段"] = "Seleccione el cambio horario";
catalog["选择日期"] = "Seleccione la fecha";
catalog["第"] = "N ? ";
catalog["天"] = "día";
catalog["周的周期不能大于52周"] = "Un período semanal no puede superar las 52 semanas.";
catalog["月的周期不能大于12个月"] = "Un periodo mensual no puede exceder de 12 meses.";
catalog["第"]="No.   ";  
catalog["天"] = "día";

catalog["时间段明细"] = "Turno Horario detalles";
catalog["确定删除该时段吗？"] = "?Está seguro de eliminar este cambio de horario?";
catalog["操作失败 {0} : {1}"] = "fallas de operación {0}: {1}";

catalog["已选择"] = "seleccionados";

catalog["日期格式输入错误"] = "formato de fecha incorrecta";
catalog["日期格式不正确！"] = "El formato de fecha que está mal! "  
catalog["夏令时名称不能为空！"] = "El nombre del horario de verano no puede ser nulo! "  
catalog["起始时间不能和结束时间相等！"] = "Hora de inicio no puede ser igual a la hora de finalización!";

catalog["请选择一个班次"] = "Seleccione un cambio";
catalog["结束日期不能小于开始日期!"] = "Fecha de finalización no puede ser anterior a la fecha de inicio!";
catalog["请输入开始日期和结束日期! "] = "Por favor, fecha de entrada de inicio y fecha final.";
catalog["只能设置一个班次! "] = "Sólo puede establecer un turno.";

catalog["当前选择设备的扩展参数获取失败，无法对该设备进行反潜设置！"] = "El dispositivo actual no seleccionados para obtener los parámetros de extensión, por lo que Marco de Lucha contra el Passback no está disponible para el dispositivo.";
catalog["服务器处理数据失败，请重试！错误码：-601"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -601.";
catalog["读取到错误的设备信息，请重试！"] = "información del dispositivo incorrecto que se lee. Por favor, inténtelo de nuevo!";
catalog["服务器处理数据失败，请重试！错误码：-602"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -602.";
catalog["或"] = " o";
catalog["反潜"] = " Anti-passback";
catalog["读头间反潜"] = "Anti-passback entre los lectores";
catalog["反潜"] = " Anti-passback";



catalog["当前门:"] = "Puerta actual:";

catalog["删除开门人员"] = "Eliminar una abertura de";
catalog["请先选择要删除的人员！"] = "Primero, seleccione la persona que desea eliminar.";
catalog["确认要从首卡常开设置信息中删除开门人员？"] = "?Está seguro de borrar la persona que abre a partir de la primera tarjeta de información de ajuste siempre abierta?";
catalog["删除开门人员成功！"] = "La persona que abre es eliminado con éxito.";
catalog["删除开门人员失败！"] = "La persona que abre no se va a eliminar.";
catalog["服务器处理数据失败，请重试！错误码：-603"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -603.";
catalog["服务器处理数据失败，请重试！错误码：-604"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -604.";


catalog["当前选择设备的扩展参数获取失败，无法对该设备进行互锁设置！"] = "El dispositivo actual no seleccionados para obtener los parámetros de extensión, de modo de bloqueo de opción no está disponible en el dispositivo.";
catalog["服务器处理数据失败，请重试！错误码：-605"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -605.";
catalog["门:"] = "Puerta:";
catalog["与"] = "y";
catalog["互锁"] = " Dispositivo de seguridad";


catalog["数据下载进度"] = "Progreso de la descarga de datos";
catalog["设备名称"] = "Nombre del dispositivo";
catalog["总进度"] = "Total de Progreso";


catalog["当前选择设备的扩展参数获取失败，无法对该设备进行联动设置！"] = "El dispositivo actual no seleccionados para obtener los parámetros de extensión, por tanto, establecer la vinculación no está disponible para el dispositivo.";
catalog["当前选择设备的扩展参数异常,请删除设备并重新添加后重试！"] = "El dispositivo seleccionado actual parámetro prórroga excepcional. Por favor, elimine el dispositivo y luego volver a agregar a intentarlo de nuevo.";
catalog["服务器处理数据失败，请重试！错误码：-606"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -606.";
catalog["服务器处理数据失败，请重试！错误码：-607"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -607.";
catalog["请输入联动设置名称！"] = "Por favor, introduzca un vínculo ajuste nombre.";


catalog["请选择地图！"] = "Por favor, elija el mapa!";
catalog["图片格式无效！"] = "Formato de imagen no válido!";

catalog["浏览多卡开门人员组："] = "Examinar la apertura de Multi-Tarjetas de personal del grupo:";
catalog[" 的人员"] = " miembro";
catalog["当前不存在多卡开门人员组"] = "No hay apertura de Multi-Tarjetas de personal del grupo en la actualidad.";
catalog["删除人员"] = "Eliminar a una persona";
catalog["确认要从多卡开门人员组中删除人员？"] = "?Está seguro de eliminar a la persona de la apertura de Multi-Tarjetas personal de grupo?";
catalog["从组中删除人员成功！"] = "La persona que se elimina del grupo de éxito.";
catalog["从组中删除人员失败！"] = "La persona deja de ser eliminado del grupo.";
catalog["服务器处理数据失败，请重试！错误码：-608"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -608.";


catalog["请至少在一个组内填入开门人数！"] = "Por favor, introduzca un número de personal en la apertura de un grupo de por lo menos.";
catalog["至少两人同时开门！"] = "Al menos dos personas puede abrir la puerta al mismo tiempo!";
catalog["最多五人同时开门！"] = "A lo sumo cinco personas puede abrir la puerta al mismo tiempo!";
catalog["人"] = "Persona";
catalog["您还没有设置多卡开门人员组！请先添加！"] = "Usted no ha establecido ninguna de las aberturas de Multi-Tarjetas de personal del grupo. Por favor, a?ade la primera.";

catalog["服务器处理数据失败，请重试！错误码：-609"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -609.";

catalog["请在文本框内输入有效的时间！"] = "Por favor, tiempo de entrada válida en el campo.";

catalog["对不起,您没有韦根卡格式设置的权限,不能进行当前操作！"] = "Lo sentimos, usted no tiene derecho a establecer el formato de tarjeta Wiegand, y no puede realizar la operación actual.";



catalog["服务器处理数据失败，请重试！错误码：-617"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -617";
catalog["添加门到当前地图"] = "A?adir puertas en el mapa actual";
catalog["请选择要添加的门！"] = "Por favor, elija las puertas que desea agregar!";
catalog["添加门成功！"] = "A?adir las puertas con éxito!";
catalog["添加门失败！"] = "Error al agregar las puertas!";
catalog["服务器处理数据失败，请重试！错误码：-618"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -618";
catalog["服务器处理数据失败，请重试！错误码：-619"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -619";
catalog["移除门成功！"] = "Retire la puerta de éxito!";
catalog["移除门失败！"] = "No se pudo quitar la puerta!";
catalog["服务器处理数据失败，请重试！错误码：-620"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -620";
catalog["添加或修改地图成功！"] = "Agregar o editar el mapa con éxito!";
catalog["确定要删除当前电子地图："] = "Confirme que se elimine el mapa actual:";
catalog["删除地图成功！"] = "Eliminar el mapa con éxito!";
catalog["删除地图失败！"] = "No se pudo eliminar el mapa!";
catalog["服务器处理数据失败，请重试！错误码：-621"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -621";
catalog["保存成功！"] = "Guardar con éxito!";
catalog["保存失败！"] = "No se pudo guardar los datos!";
catalog["服务器处理数据失败，请重试！错误码：-622"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -622";


catalog["浏览人员："] = "Examinar personal:";
catalog[" 所属权限组"] = " nivel de acceso";
catalog["当前不存在人员"] = "Ninguna persona ahora";
catalog["删除所属权限组"] = "nivel de acceso Eliminar";
catalog["请先选择要删除的权限组！"] = "Por favor seleccione el nivel de acceso que desea eliminar.";
catalog["确认要删除人员所属权限组？"] = "?Está seguro de eliminar el nivel de acceso?";
catalog["删除人员所属权限组成功！"] = "El nivel de acceso es eliminado con éxito.";
catalog["删除人员所属权限组失败！"] = "El nivel de acceso no puede ser eliminado.";
catalog["服务器处理数据失败，请重试！错误码：-610"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -610.";

catalog["数据处理进度"] = "Procesamiento de Datos Progreso";
catalog["浏览权限组："] = "Echar un nivel de acceso";
catalog[" 的开门人员"] = " personal de la apertura";
catalog["当前不存在权限组"] = "No hay nivel de acceso ahora";
catalog["从权限组中删除"] = "Eliminar del nivel de acceso";
catalog["确认要从权限组中删除人员？"] = "?Está seguro de eliminar a la persona del nivel de acceso?";
catalog["从权限组中删除人员成功！"] = "La persona que se elimina el nivel de acceso con éxito";
catalog["从权限组中删除人员失败！"] = "La persona deja de ser eliminado del nivel de acceso.";
catalog["服务器处理数据失败，请重试！错误码：-611"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -611.";

catalog["远程开门"] = "Abrir remoto";
catalog["选择开门方式"] = "Elija el modo de apertura de puerta";
catalog["开门："] = "Abra la puerta para";
catalog[" 秒"] = " Segundo (s)";
catalog["常开"] = "Normalmente abierto";
catalog["启用当天常开时间段"] = "Habilitar intradía Zona de Hora Normal Abierto";
catalog["远程关门"] = "Cierre a distancia";
catalog["选择关门方式"] = "Elija el modo de puerta de cierre";
catalog["关门"] = "Cierre la puerta";
catalog["禁用当天常开时间段"] = "Deshabilitar intradía Zona de Hora Normal Abierto";
catalog["取消报警失败！"] = "No cancela la alarma!";
catalog["取消报警成功！"] = "Cancelar la alarma con éxito!";
catalog["发送开门请求失败！"] = "No se pudo enviar la solicitud de apertura de la puerta!";
catalog["发送开门请求成功！"] = "Con éxito el envío de la solicitud de apertura de la puerta!";
catalog["发送关门请求失败！"] = "No se pudo enviar la solicitud de cierre de la puerta!";
catalog["发送关门请求成功！"] = "Con éxito el envío de la solicitud de cierre de la puerta!";
catalog["发送开关门或取消报警请求失败，请重试！"] = "El sistema no envía la apertura / cierre de puertas o solicitud de cancelación de alarma. Por favor, inténtelo de nuevo!";
catalog["当前没有符合条件的门！"] = "No hay puerta que se cumpla la condición.";
catalog["请输入有效的开门时长！必须为1-254间的整数！"] = "Por favor, introduzca una puerta abierta intervalo válido! Debe ser un número entero entre 1-254!";
catalog["离线"] = "En línea";
catalog["报警"] = "Alarma";
catalog["门开超时"] = "Apertura de tiempo de espera";
catalog["关闭"] = "Cerrado";
catalog["打开"] = "Abierto";
catalog["无门磁"] = "No hay sensor de puerta";


catalog["导出报表"] = "Exportar informe";



catalog["请输入有效的IPv4地址！"] = "Por favor, introduzca una dirección IPv4 válida.";
catalog["请输入有效的网关地址！"] = "Por favor, introduzca una dirección de puerta de enlace válido.";
catalog["请输入有效的子网掩码！"] = "Por favor, introduzca una máscara de subred válida.";

catalog["获取设备扩展参数失败，当前操作不可用！"] = "No se pudo obtener los parámetros ampliados para el dispositivo, la operación actual no está disponible!";
catalog["服务器处理数据失败，请重试！错误码：-623"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -623.";
catalog["请选择要关闭的辅助输出点！"] = "Por favor, compruebe el puerto auxiliar que desea cerrar.";

catalog["退出"] = "Salir";
catalog["正在搜索中,请等待!"] = "Búsqueda. Por favor, espere!";
catalog["服务器处理数据失败，请重试！错误码：-612"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -612.";
catalog["当前共搜索到的门禁控制器总数为："] = "El número total de paneles de control de acceso se encuentran ahora es:";
catalog["自定义设备名称"] = "Personalizar nombre del dispositivo";
catalog["设备名称不能为空，请重新添加设备！"] = "El nombre del dispositivo no puede estar vacío. Por favor, a?adir un dispositivo nuevo.";
catalog["的设备添加成功！"] = " se a?ade un dispositivo con éxito!";
catalog["已添加设备数："] = "número de dispositivos agregados";
catalog["IP地址："] = "Dirección IP";
catalog[" 已存在！"] = "ya existe!";
catalog["序列号："] = "Número de serie";
catalog["IP地址为："] = "Dirección IP:";
catalog[" 的设备添加失败！"] = " dispositivo no se a?ade!";
catalog[" 的设备添加异常！"] = " se a?ade un dispositivo excepcional.";
catalog["的设备添加成功，但设备扩展参数获取失败！"] = " se a?ade un dispositivo con éxito, pero su parámetro de extensión no pueden obtener.  ";
catalog["设备连接成功，但无数据返回，添加设备失败！"] = "El dispositivo está conectado correctamente, pero no hay datos devueltos, lo que indica que el dispositivo no se agregó.";
catalog["设备连接失败(错误码："] = "El dispositivo no se conecta (código de error:";
catalog[")，无法添加该设备！"] = "), Por lo que no se puede a?adir.";
catalog["设备连接失败(原因："] = "El dispositivo no se conecta (causa:";
catalog["服务器处理数据失败，请重试！错误码：-613"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -613.";
catalog["修改设备IP地址"] = "Modificar la dirección IP del dispositivo";
catalog["原IP地址"] = "Original de direcciones IP";
catalog["新IP地址"] = "Nueva dirección IP";
catalog["网关地址"] = "Puerta de enlace de la dirección";
catalog["子网掩码"] = "Máscara de subred";
catalog["请输入设备通讯密码:"] = "Introduzca una contrase?a de comunicación del dispositivo:";
catalog["新的IP地址不能为空！"] = "La nueva dirección IP no puede estar vacío.";
catalog["请输入一个有效的IPv4地址！"] = "Por favor, introduzca una dirección IPv4 válida.";
catalog["请输入一个有效的网关地址！"] = "Por favor, introduzca una dirección de puerta de enlace válido.";
catalog["请输入一个有效的子网掩码！"] = "Por favor, introduzca una máscara de subred válida.";
catalog["该IP地址的设备已存在或该IP地址已被使用，不能添加！请重新输入！"] = "Ya existe un aparato con una dirección IP o la dirección IP se ha utilizado, por lo que no se puede a?adir. Por favor, introduzca otra.";
catalog["修改IP地址成功！"] = "La dirección IP es modificada con éxito.";
catalog["修改IP地址失败！原因："] = "La dirección IP no puede ser modificado! Razón:";
catalog["设备连接成功，但修改IP地址失败！"] = "El dispositivo está conectado correctamente, pero la dirección IP no puede ser modificado.";
catalog["设备连接失败，故修改IP地址失败！"] = "El dispositivo no se conecta, por lo que la dirección IP no puede ser modificado.";
catalog["服务器处理数据失败，请重试！错误码：-614"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo! Código de error: -614.";
catalog["没有搜索到门禁控制器！"] = "Ningún panel de control de acceso que se encuentran.";

catalog["显示部门树"] = "Mostrar el árbol de departamento";
catalog["隐藏部门树"] = "Ocultar árbol departamento";

catalog["请选择一个调动栏位"] = "Por favor, seleccione una posición de transferencia.";

catalog["部门花名册"] = "departamento de rodillo";
catalog["学历构成分析表"] = "educación análisis de la composición";
catalog["人员流动表"] = "personal de informe el volumen de negocios";
catalog["人员卡片清单"] = "personal de lista de tarjetas de";
catalog["请选择开始日期和结束日期"] = "Por favor seleccione la fecha de inicio y fecha final.";
catalog["开始日期不能大于结束日期"] = "Fecha de inicio no puede ser posterior a la fecha de finalización.";

catalog["图片格式无效!"] = "Formato de imagen no válido";
catalog["人员编号必须为数字"] = "Personal No. debe ser numérico.";
catalog["请输入有效的E_mail!"]="Please enter a valid E_mail!   ";  
catalog["身份证号码不正确"] = "ID incorrecto número de tarjeta de";
catalog["没有可选的门禁权限组！"] = "Ningún nivel de acceso disponibles.";
catalog["指纹模板错误，请立即联系开发人员！"] = "";

catalog["修改密码"] = "Modificar la contrase?a";
catalog["旧密码："] = "Contrase?a anterior:";
catalog["新密码："] = "Nueva contrase?a:";
catalog["确认密码："] = "Confirmar contrase?a:";
catalog["最大6位整数"] ="max 6-digit integer   ";  




catalog["每次发卡数量不能超过100"] = "No más de 100 tarjetas se pueden emitir a la vez.";
catalog["起始编号长度不能超过"] = "La longitud del número de inicio no puede ser superior";
catalog["位"] = " dígitos.";
catalog["结束编号长度不能超过"] = "La longitud del número final no puede superar";
catalog["起始人员编号与结束人员编号的长度位数不同！"] = "El N ? de inicio y final son diferentes N ? de longitud.";


catalog["点击查看消息详情"] = "Haga clic para ver en detalle mensaje";
catalog["删除该消息"] = "Eliminar este mensaje";
catalog["公告详情"] = "Aviso Detalles";

catalog["保存成功!"] = "Guardado con éxito";
catalog["人员选择:"] = "Seleccione una persona:";

catalog["人员查询"] = "personal de consulta";
catalog["人员编号"] = "Personal No.";
catalog["姓名"] = "Nombre";
catalog["身份证号查询"] = "tarjeta de identificación del número de consultas";
catalog["身份证号码"] = "Número de la tarjeta de identificación";
catalog["考勤设备查询"] = "asistencia a consulta dispositivo";
catalog["离职人员查询"] = "personal de salida de consulta";
catalog["考勤原始数据查询"] = "datos de la atención inicial de consulta";
catalog["员工调动查询"] = "personal de la transferencia de consulta";
catalog["卡片查询"] = "tarjeta de consulta";
catalog["部门查询"] = "departamento de consulta";
catalog["部门编号"] = "departamento número";
catalog["部门名称"] = "Nombre del departamento";
catalog["补签卡查询"] = "anexar registro de consultas";
catalog["服务器加载数据失败,请重试!"] = "El servidor no puede cargar los datos. Por favor, inténtelo de nuevo.";

catalog["补签卡"] = "anexar registro";
catalog["补请假"] = "anexar dejar";
catalog["新增排班"] = "a?adir calendario";
catalog["临时排班"] = "programación temporal";
catalog["结束日期不能大于今天"] = "Fecha de finalización no puede ser posterior al día de hoy.";
catalog["统计只能当月日期，或者天数不能超过开始日期的月份天数！ "] = "Estadísticas involucran sólo las fechas de cada mes, o el número de días en cuestión no puede exceder el número de los días que figura en el mes de la fecha de inicio.";
catalog["请选择人员或部门"] = "Por favor, seleccione a una persona o departamento.";
catalog["统计结果详情"] = "resultado de la estadística";
catalog["每日考勤统计表"] = "cuadro estadístico de todos los días";
catalog["考勤明细表"] = "asistencia detalle";
catalog["请假明细表"] = "Deja los detalles";
catalog["考勤统计汇总表"] = "estadística de resumen";
catalog["原始记录表"] = "CA tabla de registro";
catalog["补签卡表"] = "anexar registro de la tabla";
catalog["请假汇总表"] = "Deja resumen";
catalog["请选择开始日期或结束日期!"] = "Por favor seleccione la fecha de inicio o fecha de finalización.";
catalog["开始日期不能大于结束日期!"] = "Fecha de inicio no puede ser posterior a la fecha de finalización.";
catalog["最多只能查询31天的数据!"] = "En la mayoría de los 31 días de los datos se pueden consultar.";
catalog["请在查询结果中选择人员！"] = "Por favor, una persona del resultado de la consulta.";
catalog["取消"] = "cancelar";

catalog["展开"] = "Desplegar";
catalog["收缩"] = "Veces";
catalog["自定义工作面板"] = "Personalizar Grupo de Trabajo";
catalog["锁定"] = "bloqueo";
catalog["解除"] = "desbloquear";
catalog["常用操作"] = "Operación diaria";
catalog["常用查询"] = "Común de consulta";
catalog["考勤快速上手"] = "La asistencia de inicio rápido";
catalog["门禁快速上手"] = "Control de acceso de inicio rápido";
catalog["系统提醒、公告"] = "Sistema de recordatorio y aviso";
catalog["人力构成分析"] = "Personal de análisis de la composición";
catalog["最近门禁异常事件"] = "Acceso recientes excepciones de control";
catalog["本日出勤率"] = "Promedio de Asistencia de la Jornada";
catalog["加载中......"] = "cargando ...";

catalog["是否"] = "Sí / No";
catalog["选择所有 {0}(s)"] = "Seleccionar todos los {0} (s)";
catalog["选择 {0}(s): "] = "Seleccione {0} (s):";
catalog["服务器处理数据失败，请重试！"] = "El servidor no puede procesar los datos. Por favor, inténtelo de nuevo!";
catalog["新建相关数据"] = "Crear los datos relacionados";
catalog["浏览相关数据"] = "Examinar los datos relacionados";
catalog["添加"] = "Agregar";
catalog["浏览"] = "Examinar";
catalog["编辑"] = "Editar";
catalog["编辑选定记录"] = "edición de la fila";
catalog["升序"] = "Ascender";
catalog["降序"] = "Descender";

catalog["该模型不支持高级查询功能"] = "Este modelo no es compatible con funciones avanzadas de consulta.";
catalog["高级查询"] = "Búsqueda Avanzada";
catalog["导入"] = "Importar";
catalog["请选择一个上传的文件!"] = "Por favor, seleccione un archivo para cargar.";
catalog["标题行号必须是数字!"] = "Un número de fila título debe ser un valor numérico.";
catalog["记录行号必须是数字!"] = "Un número de la fila de entrada debe ser numérico.";
catalog["请选择xls文件!"] = "Por favor seleccione un archivo xls.";
catalog["请选择csv文件或者txt文件!"] = "Por favor, seleccione un archivo csv o txt.";
catalog["文件标头"] = "archivo de cabecera";
catalog["文件记录"] = "archivo de registro";
catalog["表字段"] = "tabla presentada";
catalog["请先上传文件！"] = "Por favor, sube un archivo primero.";
catalog["导出"] = "Exportación";
catalog["页记录数只能为数字"] = "La cantidad de entradas en una página sólo puede ser un valor numérico.";
catalog["页码只能为数字"] = "El número de página sólo puede ser un valor numérico.";
catalog["记录数只能为数字"] = "La cantidad de entradas sólo puede ser un valor numérico.";
catalog["用户名"] = "Nombre de usuario";
catalog["动作标志"] = "Acción de la bandera";
catalog["增加"] = "Agregar";
catalog["修改"] = "Modificar";
catalog["删除"] = "Eliminar";
catalog["其他"] = "Otros";

catalog["门图标的位置（Top或Left）到达下限，请稍作调整后再进行缩小操作！"] = "La ubicación (parte superior o izquierda) del icono de la puerta ha llegado a mínimos, por favor, hacer algunos ajustes y luego continuar a reducir el mapa!";



catalog["信息提示"] = "Consejos";

catalog["日期"] = "fecha";

catalog["标签页不能多于6个!"] = "No puede haber más de 6 fichas.";
catalog["按部门查找"] = "Busque en nuestro Departamento";
catalog["选择部门下所有人员"] = "Seleccionar todo el personal en el Departamento";
catalog["(该部门下面的人员已经全部选择!)"] = "(Todo el personal en este departamento se han seleccionado.)";
catalog["按人员编号/姓名查找"] = "Busque en nuestro personal N ? / Nombre";
catalog["按照人员编号或姓名查找"] = "Busque en nuestro personal N ? / Nombre";
catalog["查询"] = "consulta";
catalog["请选择部门"] = "seleccione un departamento";
catalog["该部门下面的人员已经全部选择!"] = "Todo el personal en este departamento se han seleccionado.";
catalog["打开选人框"] = "abrir el cuadro de selección";
catalog["收起"] = "Cerrar";
catalog["已选择人员"] = "El personal seleccionado";
catalog["清除"] = "Borrar";
catalog["编辑还未完成，已临时保存，是否取消临时保存?"] = "La edición no se ha completado todavía, y se guarda temporalmente. ?Desea cancelar el almacenamiento temporal?";
catalog["恢复"] = "Restaurar";
catalog["会话已经过期或者权限不够,请重新登入!"] = "La sesión ha caducado o la derecha es limitado. Por favor, acceda de nuevo.";

catalog["没有选择要操作的对象"] = "Ningún objeto es seleccionado para la operación";
catalog["进行该操作只能选择一个对象"] = "Sólo un objeto puede ser seleccionado para esta operación.";
catalog["相关操作"] = "relacionados con la operación";
catalog["共"] = "Total";
catalog["记录"] = "Entrada";
catalog["页"] = "Page";
catalog["首页"] = "En primer lugar";
catalog["前一页"] = "Anterior";
catalog["后一页"] = "Siguiente";
catalog["最后一页"] = "?ltima";
catalog["选择全部"] = "Todos los";

catalog["January February March April May June July August September October November December"] = "Enero Febrero Marzo Abril Mayo Junio Julio Agosto Septiembre Octubre Noviembre Diciembre";
catalog["S M T W T F S"] = "S M T W T F S";

catalog["记录条数不能超过10000"] = "el máximo de 10.000";
catalog["当天存在员工排班时"] = "había calendario previsto en el día actual";

catalog["暂无提醒及公告信息"] = "No recordatorio y aviso";
catalog["关于"] = "Acerca de";
catalog["版本号"] = "Número de versión";
catalog["本系统建议使用浏览器"] = "Los navegadores que se recomienda";
catalog["显示器分辨率"] = "Resolución del monitor";
catalog["及以上像素"] = "píxeles y, sobre";
catalog["软件运行环境"] = "El ambiente para el funcionamiento de este software";
catalog["系统默认"] = "Por defecto";

catalog["photo"] = "Foto";
catalog["table"] = "Cuadro";

catalog["此卡已添加！"] = "Esta tarjeta ha sido agregado!";
catalog["卡号不正确！"] = "El número de la tarjeta está mal!";
catalog["请输入要添加的卡号！"] = "Por favor introduce el número de la tarjeta!";
catalog["请选择刷卡位置！"] = "Por favor, seleccione la posición de deslizar la tarjeta!";
catalog["请选择人员！"] = "Seleccione una persona!";
catalog["table"] = "Cuadro";
catalog["table"] = "Cuadro";
catalog["首字符不能为空!"]="  El primer carácter no puede estar vacío!";
catalog["密码长度必须大于4位!"]="  longitud de la contrase?a debe ser mayor que 4!";

catalog["当前列表中没有卡可供分配！"] = "No hay tarjeta puede ser asignado en la lista actual!";
catalog["当前列表中没有人员需要分配！"] = "No hay necesidad de asignar la tarjeta en la lista actual!";
catalog["没有已分配人员！"] = "No hubo persona que ha sido assgined!";
catalog["请先点击停止读取！"] = "Por favor, dejen de leer el número de tarjeta de primera!";
catalog["请选择需要分配的人员！"] = "Por favor, seleccione la persona que debe asignar la tarjeta!";

catalog["请选择一个介于1到223之间的数值！"] = "Por favor, especifique un valor entre 1 y 223!";
catalog["备份路径不存在，是否自动创建？"] = "La ruta de copia de seguridad no existe, crear de forma automática?";
catalog["处理中"] = "Procesamiento " ;
catalog["是"] = "Sí";
catalog["否"] = "No";


catalog["已登记指纹"] = "Registrado huella digital:";

catalog["不合法"]="Ilegales";

catalog["通讯密码"] = "Contraseña de comunicación";

catalog[ "新增时删除设备中数据"] = "Añadir a eliminar los datos del dispositivo";

catalog["您选择了[新增时删除设备中数据]，系统将自动删除设备中的数据(事件记录除外)，确定要继续？"] = "Selecciona [Añadir a eliminar dispositivo de datos], el sistema automáticamente eliminará los datos del dispositivo (excepto el registro de sucesos), es seguro de que desea continuar?";