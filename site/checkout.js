vtotal = 0
ttotal = 0
cstate = 0
lcstate = 0
vline = 0
otheramt = 0

// using the sound sample length to limit button-presses
function readysnd(snd) {
    return ($('audio#' + snd)[0].paused)
}
lastendedevent = 0
function playsnd(snd,endfunc=0) {
    if (lastendedevent) {
        $('audio#'+snd)[0].removeEventListener("ended",lastendedevent)
    }
    if (endfunc) {
        $('audio#'+snd)[0].addEventListener("ended",endfunc)
        lastendedevent = endfunc
    }
    $('audio#'+snd)[0].play()
}    
function playthen(snd,btn) {
    $(btn).addClass("checkitemselected")
    playsnd(snd,function() {
        $(btn).removeClass("checkitemselected")
    })

}

function updateprices() {
    $(".checkitem").each(function() {
        let price = $(this).data("price")
        if (price > 0)
            $(this).find(".checkitemprice").text(price.toFixed(2))
        else if (price ==0)
            $(this).find(".checkitemprice").text("")
        else 
            $(this).find(".checkitemprice").text(vtotal.toFixed(2))
    })
    if (cstate == 0) {
        if ($(".checktoprighttop .checkrightline").length == 0) 
            $("#checkcancel span").text("")
        else
            $("#checkcancel span").text("Undo")
        $("#checkother").removeClass("checkhide")
        $("#checkother span").text("Enter Price")
        if (vtotal > 0) {
            $("#checkgo span").text("Checkout")
        } else {
            $("#checkgo span").text("")
        }
    } else if (cstate == 1) {
        $("#checkcancel span").text("Cancel")
        $("#checkother").addClass("checkhide")
        if (ttotal >= vtotal) {
            $("#checkgo span").text("Checkout")
        } else {
            $("#checkgo span").text("")
        }
    } else if (cstate == 2) {
        $("#checkcancel span").text("Cancel")
        $("#checkother").removeClass("checkhide")
        if (otheramt > 0)
            $("#checkother span").text("Add Item")
        else
            $("#checkother span").text("")
    }
}

function maketotal(label) {
    let retdiv = $("<div/>")
        .addClass("checkrighttotal checkrightline")
    retdiv.append($("<span/>")
        .addClass("checkrightlabel")
        .text(label)
    )
    retdiv.append($("<span/>")
        .addClass("checkrightprice")
        .text("")
    )
    return retdiv
}
totaldiv = maketotal("Total")
changediv = maketotal("Change")
tenderdiv = maketotal("Tendered")
function settotal(tdiv,value) {
    tdiv.find(".checkrightprice").text(value.toFixed(2))
}
function getprice(price) {
    price = price.replace("£","")
    return parseFloat(price)
}
function addvend(type,label,price,color) {
    parentdiv = $("<div/>")
        .addClass("checkrightline")
        .attr("data-price",price)
        .attr("data-type",type)
    parentdiv.append($("<div/>")
        .addClass("checkrightlabel")
        .text(label)
    )        
    parentdiv.append($("<div/>")
        .addClass("checkrightprice")
        .text(price.toFixed(2))
    )
    parentdiv.css("color",color)
    $(".checktoprighttop").append(parentdiv)
    return parentdiv
}
function updvend(vendline,price) {
    $(vendline).data("price",price).find(".checkrightprice").text(price)
}
function addvtotal(amt) {
    vtotal += amt
    settotal(totaldiv,vtotal)
}
function itemclick() {
    if (readysnd("pop")) {
        thisprice = $(this).data("price")
        if (cstate == 0) {
            addvend($(this).parent().data("type"),$(this).find(".checkitemlabel").text(),thisprice,$(this).css("background-color"))
            addvtotal(thisprice)
            $(".checktoprightbottom").append(totaldiv)
            playthen("pop",this)
        } else if (cstate == 1) {
            if ($(this).data("type") == "other") {
                settotal(tenderdiv,vtotal)
                ttotal = vtotal
                tenderdiv.find(".checkrightlabel").text($(this).find(".checkitemlabel").text())
                playthen("pop",this)
            } else {
                if (ttotal >= vtotal && tenderdiv.find(".checkrightlabel").text() != "Cash") 
                    ttotal = thisprice
                else if (ttotal < vtotal)
                    ttotal += thisprice
                else
                    return
                settotal(tenderdiv,ttotal)
                tenderdiv.find(".checkrightlabel").text("Cash")
                playthen("pop",this)
            }
            settotal(changediv,vtotal-ttotal)
            if (vtotal > ttotal) {
                tenderdiv.css("color","red")
                changediv.find(".checkrightlabel").text("Owed")
                changediv.css("color","red")
            } else {
                tenderdiv.css("color","limegreen")
                changediv.find(".checkrightlabel").text("Change")
                changediv.css("color","limegreen")
            }
            $(".checktoprightbottom").append(tenderdiv)
            $(".checktoprightbottom").append(changediv)
        } else {
            $(".checktoprightbottom").append(totaldiv)
            addvtotal(0-otheramt/100)
            let amt = $(this).find(".checkitemlabel").text()
            if (amt == "<<") {
                if (otheramt > 0) {
                    otheramt = Math.trunc(otheramt / 10)
                    playthen("pop",this)
                }
            } else if (amt == "00") {
                otheramt *= 100
                if (otheramt > 0)
                    playthen("pop",this)
            } else {
                otheramt = otheramt * 10 + parseInt(amt)
                if (otheramt > 0)
                    playthen("pop",this)
            }
            if (vline) {
                updvend(vline,(otheramt/100).toFixed(2))
                addvtotal(otheramt/100)
            }
        }
    }
    updateprices()
}
function changepage(pg) {
    cstate = pg
    for (i=0;i<3;i++) {
        if (i == cstate)
            $(".checklayer"+i).removeClass("checkhide")
        else
            $(".checklayer"+i).addClass("checkhide")
    }
}
function checkback() {
    if (readysnd("undo")) {
        if (cstate == 0) {
            let remline = $(".checktoprighttop .checkrightline").last()
            if (remline.length) {
                vtotal -= remline.data("price")
                settotal(totaldiv,vtotal)
                remline.remove()
                playsnd("undo")            
            }
        } else if (cstate == 1) {            
            ttotal = 0
            changepage(0)
            tenderdiv.remove()
            changediv.remove()
            $(".checktoprightbottom").append(totaldiv)
            playsnd("undo")
        } else {
            addvtotal(0-otheramt/100)
            vline.remove()
            changepage(lcstate)
            playsnd("undo")            
        }
        updateprices()
    }    
    if ($(".checktoprighttop .checkrightline").length == 0) {
        totaldiv.remove()
    }
}
function checkother() {
    if (readysnd("pop")) {
        if (cstate != 2) {
            lcstate = cstate
            if (cstate == 0) {
                otheramt = "0"
                vline = addvend("Other","Other",0,"Orange")            
            }
            changepage(2)        
            playsnd("pop")
        } else {
            if (otheramt != 0) {
                changepage(lcstate)
                playsnd("pop")
            }
        }
        updateprices()
    }
}
function checkgo() {
    if (readysnd("beep")) {
        if ((cstate == 0 || cstate == 2)  && vtotal > 0) {
            settotal(totaldiv,vtotal)
            $(".checktoprighttop").append(totaldiv)
            changepage(1)
            playsnd("beep")
        } else if (cstate == 1 && vtotal <= ttotal) {
            let transdata = {
                "sales": [],
                "tender": []
            }
            $(".checktopright .checkrightline").each(function() {
                let type = $(this).data("type")
                if (!type) {
                    transdata["tender"].push($(this).find(".checkrightprice").text())            
                } else {
                    transdata["sales"].push({
                        "type": type,
                        "price": $(this).data("price")
                    })
                }
                $(this).remove()
            })
            vtotal = 0
            ttotal = 0
            changepage(0)
            tenderdiv.remove()
            changediv.remove()
            totaldiv.remove()
            $.ajax("/checkoutlog", {
                data : JSON.stringify(transdata),
                contentType : 'application/json',
                type : 'POST'
            })
            playsnd("beep")
        }
        updateprices()
    }
}
$(document).ready(function() {
    $(".checklayertender").addClass("checkhide");
    $(".checkitem").on("click",itemclick)
    $("#checkother").on("click",checkother)
    $("#checkcancel").on("click",checkback)
    $("#checkgo").on("click",checkgo)
    changepage(0)
    updateprices()
})
