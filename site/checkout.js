vtotal = 0
ttotal = 0
cstate = 0 // 0 - vend, 1 - payment, 2 - manual input, 3 - next customer, 4 - processing data to server, 5 swipe card, 6 - enter name
otheramt = 0
lastendedevent = 0
cotext = ""
cardswiped = false

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

function flipborder(obj,from,to) {
    obj.css("border-color",from)
    setTimeout(function() {
        obj.css("border-color",to)
    },150)
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
    if (cstate == 5) {
        $(".checkoutcard").css("display","inline-flex").css("pointer-events", "auto")
    } else if (cstate == 6) {
        $(".checkoutcard").css("display","none").css("pointer-events", "none")
        $(".checkoutboard").css("display","inline-flex").css("pointer-events", "auto")
    } else {
        $(".checkoutcard,.checkoutboard").css("display","none").css("pointer-events", "none")
    }
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
        $("#checkgo span").text("")
        $("#checkcancel span").text("Cancel")
        $("#checkother").removeClass("checkhide")
        if (otheramt > 0)
            $("#checkother span").text("Done")
        else
            $("#checkother span").text("")
    } else if (cstate == 3) {
        $("#checkcancel span").text("")
        $("#checkgo span").text("Next Customer")
    } else if (cstate == 4) {
        $("#checkgo span").text("Processing...")
    } else if (cstate == 5) {
        $("#checkgo span").text("Skip Card")
        $("#checkcancel span").text("Cancel")
        $("#checkother").addClass("checkhide")
    } else if (cstate == 6) {
        $("#checkgo span").text("Add Member")
        $("#checkcancel span").text("Cancel")
        $("#checkother").addClass("checkhide")
    }
    $("#checkouttext").html("&nbsp;" + cotext)
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
        .text(label).append($("<div></div>")
            .addClass("checkrightlabeltext"))
    )        
    parentdiv.append($("<div/>")
        .addClass("checkrightprice")
        .text(price.toFixed(2))
    )
    parentdiv.css("color",color)
    $(".checktoprighttop").append(parentdiv)
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
                if ($(this).data("type") == "Subscription" && !cardswiped) {
                    cstate = 5
                }
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
            let price = otheramt/100
            lastvend().data("price",price).find(".checkrightprice").text(price.toFixed(2))
            addvtotal(price)
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
function checkcancel() {
    if (readysnd("undo")) {
        flipborder($("#checkcancel"),"white","")
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
        } else if (cstate == 5 || cstate == 6) {
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
        flipborder($("#checkother"),"white","")
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
function updatename(nm,isnew=false,ex="") {
    lastvend().attr("data-membername",nm)
    lastvend().attr("data-isnew",isnew)
    let lv = lastvend().find(".checkrightlabeltext").text(nm + " - " + ex)
}
function checkgo() {
    if (readysnd("beep")) {
        flipborder($("#checkgo"),"white","")
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
                    dtt = {}
                    for (dt in $(this).data())
                        dtt[dt] = $(this).data(dt)
                    transdata["sales"].push(dtt)
                }
            })
            transdata["tender"]["Paid"] = tenderdiv.find(".checkrightlabel").text()
            transdata["tender"]["Total"] = vtotal
            transdata["tender"]["Change"] = vtotal-ttotal
            cstate = 4
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
        } else if (cstate == 5) {            
            updatename("",true)
            cstate = 0
            playsnd("beep")
        } else if (cstate == 6) {
            updatename(cotext,true)
            cstate = 0
            playsnd("beep")
        }
        updateprices()
    }
}
$(document).ready(function() {
    $(".checklayertender").addClass("checkhide");
    $(".checkitem").on("click",itemclick)
    $("#checkother").on("click",checkother)
    $("#checkcancel").on("click",checkcancel)
    $("#checkgo").on("click",checkgo)
    $(window).on("mousedown touchdown",function(e) {
        $(".debug").text(e.screenX + " - " + e.screenY + " - " + e.timeStamp)
    })
    changepage(0)
    updateprices()

    $(".modal__header").append(
        $("<div>",{id: "footright",text: ""})
    )
    cardinput = ""
    lastcardinput = 0
    $(window).on("keydown",function(e) {
        let nw = new Date().getTime()
        if (nw - lastcardinput > 3000)
            cardinput = ""
        if (e.key == "Enter" && cardinput != "") {
            if (cstate == 5 || cstate == 0)  {
                lastvend().attr("data-card",cardinput)
                $.ajax("/checkcard", {
                    data : {"card": cardinput},
                    type : 'POST',
                    success: function(response) {
                        if (cstate == 0) {
                            cardswiped = true
                            btntopress = $("#Subscription"+response["vip"])
                            if (btntopress.length) {
                                btntopress.click()
                                lastvend().attr("data-card",cardinput)
                            } else
                                playsnd("undo")
                            cardswiped = false
                        }
                        cardinput = ""
                        if (response == "Not Found") {
                            if (cstate == 5) {
                                updatename("")
                                cotext = ""
                                cstate = 6                                
                            } else {
                                playsnd("undo")
                            }
                        } else {
                            updatename(response["name"],false,response["newexpires"])
                            cstate = 0                                
                        }
                        updateprices()
                    },
                    error: function(xhr, ajaxOptions, thrownError) {
                        cardinput = ""
                        cstate = 0 // TODO not sure what to do here - why would this possibly fail???
                        updateprices()
                    }
                })                                        
            }
        } else if ("0123456789".includes(e.key))
            cardinput += e.key
        lastcardinput = nw
    })
    checkoutboard = "ABCDEFGHIJKLMNOPQRSTUVWXYZ <"
    chrows = 4
    chrowl = Math.round(checkoutboard.length/chrows,0)
    for (i=0;i < chrows;i++) {
        let row = $("<div>",{class: "checkoutboardrow"})
        for (j = 0; j < chrowl;j++) {
            row.append(                
                $("<div>",{class: "checkoutboardkey",text: checkoutboard[i*chrowl+j]})
            )
        }
        $("#checkoutletters").append(row)
    }
    $(".checkoutboardkey").on("mousedown touchdown",function(e) {
        if (readysnd("pop")) {
            let lt = $(this).text()
            if (lt == "<")
                cotext = cotext.substr(0,cotext.length-1)
            else if (lt != " " || (cotext != "" && cotext.substr(cotext.length-1,1)) != " ")
                cotext += $(this).text()            
            playthen("pop",this)
            updateprices()
        }
    })
})
