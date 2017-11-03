/**
 * Created by jschn on 17/04/2017.
 */

function getPos(event){
    var img = $("#img");
    var posX = event.offsetX?(event.offsetX):event.pageX-img.offsetLeft;
    var posY = event.offsetY?(event.offsetY):event.pageY-img.offsetTop;
    document.getElementById("imgcords").innerHTML = "Your Mouse Position Is : " + posY + " and " + posX;
}

function stopTracking(){
    document.getElementById("imgcords").innerHTML="";
}

function fillValues(event){
    var img = $("#img");
    var width = event.offsetX?(event.offsetX):event.pageX-img.offsetLeft;
    var height = event.offsetY?(event.offsetY):event.pageY-img.offsetTop;
    if (document.getElementById("ulx").value == "" || document.getElementById("uly").value == ""){
        document.getElementById("ulx").value = height;
        document.getElementById("uly").value = width;
    } else {
        if (document.getElementById("urx").value == "" || document.getElementById("ury").value == ""){
            document.getElementById("urx").value = height;
            document.getElementById("ury").value = width;
        } else {
            if (document.getElementById("lrx").value == "" || document.getElementById("lry").value == ""){
                document.getElementById("lrx").value = height;
                document.getElementById("lry").value = width;
            } else {
                if (document.getElementById("llx").value == "" || document.getElementById("lly").value == ""){
                    document.getElementById("llx").value = height;
                    document.getElementById("lly").value = width;
                }
            }
        }
    }
}
