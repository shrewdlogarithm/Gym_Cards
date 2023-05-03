vtotal = 0
ttotal = 0
cstate = 0
otheramt = 0
lastendedevent = 0

// using the sound sample length to limit button-presses
function readysnd(snd) {
    return ($('audio#' + snd)[0].paused)
}
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
function vendlines() {
    return $(".checktoprighttop .checkrightline").length
}
function lastvend() {
    return $(".checktoprighttop .checkrightline").last()
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
        if (!vendlines()) 
            $("#checkcancel span").text("")
        else
            $("#checkcancel span").text("Remove Last Item")
        $("#checkother").removeClass("checkhide")
        if (vendlines() > 9)
            $("#checkother span").text(">> MAX ENTRIES <<")
        else
            $("#checkother span").text("Enter Any Price")
        if (vtotal > 0) {
            $("#checkgo span").text("Checkout")
        } else {
            $("#checkgo span").text("")
        }
    } else if (cstate == 1) {
        $("#checkcancel span").text("Cancel")
        $("#checkother").addClass("checkhide")
        if (ttotal >= vtotal) {
            $("#checkgo span").text("Open Drawer")
        } else {
            $("#checkgo span").text("")
        }
    } else if (cstate == 2) {
        $("#checkcancel span").text("Cancel")
        $("#checkgo span").text("")
        $("#checkcancel span").text("Cancel")
        $("#checkother").removeClass("checkhide")
        if (otheramt > 0)
            $("#checkother span").text("Done")
        else
            $("#checkother span").text("")
    } else if (cstate == 3) {
        $("#checkgo span").text("Next Customer")
    } else if (cstate == 4) {
        $("#checkgo span").text("Processing...")
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
        .attr("data-label",label)
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
}
function updvend(vendline,price) {
    $(vendline).data("price",price).find(".checkrightprice").text(price.toFixed(2))
}
function addvtotal(amt) {
    vtotal += amt
    settotal(totaldiv,vtotal)
}
function itemclick() {
    if (readysnd("pop")) {
        thisprice = $(this).data("price")
        if (cstate == 0) {
            if (checkmaxvendlines()) {
                addvend($(this).parent().data("type"),$(this).find(".checkitemlabel").text(),thisprice,$(this).css("background-color"))
                addvtotal(thisprice)
                $(".checktoprightbottom").append(totaldiv)
                playthen("pop",this)
            }
        } else if (cstate == 1) {
            if ($(this).data("price") == -1) {
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
        } else if (cstate == 2) {
            addvtotal(0-otheramt/100)
            let amt = $(this).find(".checkitemlabel").text()
            if (amt == "<<<") {
                if (otheramt > 0) {
                    otheramt = Math.trunc(otheramt / 10)
                    playthen("pop",this)
                }
            } else if (amt == "00") {
                if (otheramt < 100) {
                    otheramt *= 100
                    if (otheramt > 0)
                        playthen("pop",this)
                }
            } else {
                if (otheramt < 1000) {
                    otheramt = otheramt * 10 + parseInt(amt)
                    if (otheramt > 0)
                        playthen("pop",this)
                }
            }
            if (otheramt > 0) {
                $(".checktoprightbottom").append(totaldiv)                
            }
            updvend(lastvend(),otheramt/100)
            addvtotal(otheramt/100)
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
            let remline = lastvend()
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
        } else if (cstate == 2) {
            addvtotal(0-otheramt/100)
            lastvend().remove()
            changepage(0)
            playsnd("undo")            
        }
        updateprices()
    }    
    if (vendlines() == 0) {
        totaldiv.remove()
    }
}
function checkmaxvendlines() {
    if (vendlines() > 9) {
        playsnd("undo")
        return false
    } else   
        return true
}
function checkother() {
    if (readysnd("pop")) {
        if (cstate == 0) {
            if (checkmaxvendlines()) {
                if (cstate == 0) {
                    otheramt = "0"
                    addvend("Other","Other",0,"Orange")            
                }
                changepage(2)        
                playsnd("pop")
            }
        } else {
            if (otheramt != 0) {
                changepage(0)
                playsnd("pop")
            }
        }
        updateprices()
    }
}
function checkgo() {
    if (readysnd("beep")) {
        if (cstate == 0  && vtotal > 0) {
            settotal(totaldiv,vtotal)
            $(".checktoprighttop").append(totaldiv)
            changepage(1)
            playsnd("beep")
        } else if (cstate == 1 && vtotal <= ttotal) {
            let transdata = {
                "sales": [],
                "tender": {}
            }
            $(".checktopright .checkrightline").each(function() {
                if (!$(this).hasClass("checkrighttotal")) {
                    transdata["sales"].push({
                        "type": $(this).data("type"),
                        "label": $(this).data("label"),
                        "price": $(this).data("price")
                    })
                }
            })
            transdata["tender"]["Paid"] = tenderdiv.find(".checkrightlabel").text()
            transdata["tender"]["Total"] = vtotal
            transdata["tender"]["Change"] = vtotal-ttotal
            cstate = 4
            updateprices()
            $.ajax("/checkoutlog", {
                data : JSON.stringify(transdata),
                contentType : 'application/json',
                type : 'POST',
                success: function(response) {
                    cstate = 3
                    updateprices()
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    playsnd("undo")
                    cstate = 1
                    updateprices()
                }
            })            
            playsnd("beep")
        } else if (cstate == 3) {
            vtotal = 0
            ttotal = 0            
            $(".checktopright .checkrightline").each(function() {
                $(this).remove()
            })
            changepage(0)
            tenderdiv.remove()
            changediv.remove()
            totaldiv.remove()
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
