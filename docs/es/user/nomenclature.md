[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | es | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Nomenclatura

Los términos que usan SAJ Local, las tarjetas del panel y la documentación, cada uno con un significado de una línea. Toda traducción de la integración, de las tarjetas y de la documentación usa un único término para cada cosa de esta lista. La sección [Idiomas](../../../custom_components/saj_local/docs/features.md#languages) de la lista de funciones de la integración indica los idiomas en los que se distribuye SAJ Local.

## Equipos y lecturas de SAJ

| Término | Significado |
| --- | --- |
| Inversor | La unidad SAJ que convierte la corriente continua solar y de la batería en corriente alterna para la casa y la red. |
| HS3 | El modelo de inversor híbrido SAJ HS3, un modelo trifásico. |
| H2 | El modelo de inversor híbrido SAJ H2, un modelo monofásico. |
| Modelo | El tipo de inversor que SAJ Local usa para elegir la lista de registros: Automático, HS3 o H2. |
| Automático | La opción de modelo que reconoce el modelo a partir del tipo de dispositivo que informa el inversor. |
| Equipo opcional | El equipo que una instalación puede tener o no: una batería, el Contador A, el Contador B, un cargador de VE o un sistema en paralelo. |
| Instalado | El ajuste que indica a SAJ Local que un equipo opcional está instalado. |
| No instalado | El ajuste que indica a SAJ Local que un equipo opcional no está instalado. |
| Batería | El almacenamiento de energía conectado al inversor. |
| Módulo de batería | Un módulo de batería dentro de una batería, que se muestra como Módulo seguido de un número. |
| Estado de carga | Cuán llena está la batería, en porcentaje. |
| Reserva | La carga de la batería que el inversor guarda y por debajo de la cual no descarga. |
| Solar | La potencia que producen los paneles solares. |
| String solar | Un grupo de paneles solares conectados en serie y unidos a una entrada del inversor. |
| Fase | Un conductor de la alimentación de corriente alterna. |
| Red | La red eléctrica pública a la que está conectada la casa. |
| Importando | Tomar potencia de la red. |
| Exportando | Enviar potencia a la red. |
| Cargando | Meter potencia en la batería. |
| Descargando | Sacar potencia de la batería. |
| Casa | La potencia que consume la casa. |
| Carga de respaldo | Las cargas que siguen alimentadas desde la batería y los paneles solares cuando falla la red. |
| Contador A | El primer contador eléctrico que se puede conectar al inversor. |
| Contador B | El segundo contador eléctrico que se puede conectar al inversor. |
| Cargador de VE | Un cargador de vehículos eléctricos conectado al inversor. |
| Sistema en paralelo | Varios inversores que trabajan juntos como un solo sistema. |
| Fallo | Un problema que informa el equipo, con un registro Modbus y un bit. |
| Borrar fallo | El botón que pide al inversor que borre un fallo informado. |
| Estado de funcionamiento | El estado en que se encuentra el inversor, por ejemplo en marcha o en espera. |
| Modo | El modo de funcionamiento del inversor, por ejemplo horario programado. |
| Horario programado | El modo en el que la batería se carga y se descarga en las franjas que defines. |
| Franja | Un periodo del horario programado para cargar, descargar o para el cargador de VE. |
| EMS | Las funciones de gestión de energía del inversor, que mantienen un objetivo de potencia desde el exterior. |
| Latido de EMS | La frecuencia con la que SAJ Local lee los objetivos de EMS para mantener activas las funciones de EMS. |
| Tiempo de espera de EMS | El tiempo tras el cual el inversor termina una función de EMS que no se mantiene activa. |
| Protección contra corriente inversa | La protección del inversor contra el flujo de potencia de vuelta al inversor, que las funciones de EMS desactivan. |
| Control de potencia | Mantener la batería, la conexión a la red o el inversor a una potencia fija. |
| Objetivo de potencia | La potencia que mantiene una función de control de potencia. |
| Programación | Las horas a las que se ejecuta una función de control de potencia. |
| Permitir control | El ajuste que permite a Home Assistant cambiar los ajustes del inversor. |
| Control | La capacidad de cambiar los ajustes del inversor, en lugar de solo leerlo. |
| Registro Modbus | Una posición de memoria numerada del inversor que contiene una lectura o un ajuste. |
| Registro Modbus rechazado | Un registro Modbus al que el inversor se niega a responder. |
| Modbus TCP | El protocolo de red que SAJ Local usa para comunicarse con el inversor. |
| Host | La dirección de red del inversor. |
| Puerto | El puerto de red del inversor, 502 por defecto. |
| ID de unidad | La dirección Modbus del inversor, de 1 a 247. |
| Módulo de comunicación | La parte del inversor que responde a las solicitudes de red. |
| Bloque | Un intervalo de registros Modbus que se lee con una sola solicitud. |
| Tiempo real | El bloque de lecturas que cambian de segundo en segundo. |
| Promedios de cinco minutos | El bloque de lecturas que el inversor promedia durante cinco minutos. |
| Energía | El bloque de lecturas de energía producida y consumida, como la energía de hoy. |
| Identidad | El modelo, el número de serie y las versiones que informa el inversor. |

## Conceptos de SAJ Local

| Término | Significado |
| --- | --- |
| Sistema | Un inversor, con su equipo, añadido a Home Assistant. |
| Instalación | Una entrada de configuración de SAJ Local, que es un sistema. |
| Prefijo | Texto opcional que se añade a los ID de entidad de una instalación, usado cuando hay más de un sistema. |
| Sondeo | Leer el inversor a intervalos. |
| Grupo de sondeo | Un conjunto elegido de entidades que SAJ Local lee más rápido o más despacio que el intervalo por defecto. |
| Intervalo de actualización | Los segundos entre dos lecturas del inversor, que se muestra como «Segundos entre actualizaciones». |
| Carga de solicitudes | El número de solicitudes por minuto que SAJ Local envía al inversor, frente al límite de 40 en 60 segundos. |
| Presupuesto | El límite de la carga de solicitudes. |
| Sustitución de modelo | Pasar un sistema a un inversor nuevo, o entre un H2 y un HS3, conservando el historial. |
| Sin verificar | Un modelo que se eligió a mano y no se pudo comprobar con el tipo de dispositivo. |
| Descarga de diagnósticos | El archivo que contiene una instantánea del sistema, segura para la privacidad, para un informe de error. |
| Registro de depuración | La opción que escribe líneas de registro detalladas para encontrar un problema. |
| Tarjeta del panel | Una tarjeta que SAJ Local añade a los paneles de Home Assistant. |
| Tarjeta de flujo de potencia | La tarjeta que muestra la potencia en vivo entre solar, batería, red y casa. |
| Tarjeta de estado | La tarjeta que muestra el estado de funcionamiento, el modo, las lecturas clave y los fallos. |
| Tarjeta de fallos | La tarjeta que lista los fallos activos. |
| Tarjeta de batería | La tarjeta que muestra las lecturas de la batería y una fila por módulo. |
| Tarjeta de controles | La tarjeta que muestra los controles compartidos del sistema. |
| Tarjeta de programación | La tarjeta que muestra las franjas con una línea de tiempo semanal. |
| Función de tarjeta mosaico de días de la semana | Los siete botones de días que se pueden añadir a una tarjeta mosaico. |
| Insignia de estado | La insignia que muestra el estado de funcionamiento y el número de fallos activos. |

## Conceptos de Home Assistant

| Término | Significado |
| --- | --- |
| Home Assistant | El software de domótica del que SAJ Local es una integración. |
| Integración | Software que conecta un tipo de dispositivo o servicio a Home Assistant. |
| HACS | La tienda de la comunidad de Home Assistant (Home Assistant Community Store), usada para instalar SAJ Local. |
| Repositorio personalizado | Un repositorio que no está en la lista predeterminada de HACS y que se añade a HACS mediante su dirección; la insignia «HACS personalizado» de los README marca SAJ Local como uno de ellos. |
| Flujo de configuración | El diálogo de configuración que añade un sistema. |
| Entrada de configuración | La configuración guardada de un sistema. |
| Subentrada | Una parte de una entrada de configuración que se añade y se cambia por separado, como un grupo de sondeo o una programación de potencia. |
| Configurar | El botón de una integración que abre sus opciones. |
| Dispositivos y servicios | La página de ajustes de Home Assistant que lista integraciones, dispositivos y entidades. |
| Ajustes | La página de Home Assistant para configurar Home Assistant. |
| Dispositivo | El registro de Home Assistant de un equipo que contiene entidades. Cada sistema es un dispositivo. |
| Entidad | Una lectura, un ajuste o una orden que muestra Home Assistant. |
| ID de entidad | El identificador único de una entidad, como sensor.saj_pv_power. |
| Sensor | Una entidad que muestra una lectura. |
| Sensor binario | Una entidad que está encendida o apagada, como un fallo. |
| Número | Una entidad que contiene un número que se puede cambiar. |
| Seleccionar | Una entidad que contiene una opción de una lista. |
| Interruptor | Una entidad que se puede encender o apagar. |
| Hora | Una entidad que contiene una hora del día. |
| Botón | Una entidad que ejecuta una acción al pulsarla. |
| Habilitada por defecto | Si una entidad está activada cuando se añade el sistema. |
| Deshabilitada | Una entidad que Home Assistant no lee ni muestra. |
| Reparación | Un aviso en Home Assistant de que algo requiere tu acción, con un botón Reparar. |
| Panel | Una pantalla de Home Assistant formada por tarjetas. |
| Tarjeta | Un bloque de un panel. |
| Tarjeta mosaico | Una tarjeta de Home Assistant que muestra una entidad y a la que se pueden añadir funciones. |
| Insignia | Un elemento pequeño de la fila de insignias en la parte superior de un panel. |
| Automatización | Una regla que hace que Home Assistant actúe cuando ocurre algo. |
| Ayudante | Una entidad de Home Assistant que creas tú mismo, como un ayudante de programación. |
| Área | Una habitación o lugar en el que se agrupan los dispositivos. |
| Tema | Los colores de la interfaz de Home Assistant. |
| Idioma | El idioma que un usuario de Home Assistant elige en la página del perfil. |
| Recargar | Reiniciar una integración sin reiniciar Home Assistant. |
| Reiniciar | Reiniciar Home Assistant. |
| Herramientas para desarrolladores | Las páginas de Home Assistant para comprobar estados y llamar a acciones. |
| Registros | El registro de mensajes de Home Assistant. |
