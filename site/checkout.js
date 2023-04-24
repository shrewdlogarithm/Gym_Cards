cstate = 0
vtotal = 0
ttotal = 0

// using the sound sample length to limit button-presses
function readysnd(snd) {
    return ($('audio#' + snd)[0].paused)
}
function playsnd(snd) {
    $('audio#'+snd)[0].play()
}    

function updateprices() {
    $(".checkitem").each(function() {
        let price = $(this).data("price")
        if (price != -1)
            $(this).find(".checkitemprice").text(price.toFixed(2))
        else
            $(this).find(".checkitemprice").text(vtotal)
    })
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
totaldiv = maketotal("TOTAL")
changediv = maketotal("Change")
tenderdiv = maketotal("Tendered")
function settotal(tdiv,value) {
    tdiv.find(".checkrightprice").text(value.toFixed(2))
}
function getprice(price) {
    price = price.replace("£","")
    return parseFloat(price)
}
function itemclick() {
    if (readysnd("pop")) {
        thisprice = $(this).data("price")
        if (cstate == 0) {
            parentdiv = $("<div/>")
                .addClass("checkrightline")
                .attr("data-price",thisprice)
                .attr("data-type",$(this).parent().data("type"))
            parentdiv.append($("<div/>")
                .addClass("checkrightlabel")
                .text($(this).find(".checkitemlabel").text())
            )        
            parentdiv.append($("<div/>")
                .addClass("checkrightprice")
                .text(thisprice.toFixed(2))
            )
            vtotal += thisprice
            settotal(totaldiv,vtotal)
            parentdiv.css("color",$(this).css("background-color"))
            $(".checktoprighttop").append(parentdiv)
            $(".checktoprightbottom").append(totaldiv)
            playsnd("pop")
        } else {
            let ctotal = 0
            if ($(this).data("type") == "other") {
                settotal(tenderdiv,vtotal)
                ttotal = 0
                tenderdiv.find(".checkrightlabel").text($(this).find(".checkitemlabel").text())
            } else if (ttotal<vtotal) {
                ttotal += thisprice
                settotal(tenderdiv,ttotal)
                ctotal = vtotal-ttotal
                tenderdiv.find(".checkrightlabel").text("Cash")
            } else {
                return
            }
            settotal(changediv,ctotal)
            if (ctotal > 0) {
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
            playsnd("pop")    
        }
    }
    updateprices()
}
function checkback() {
    if (readysnd("beep")) {
        if (cstate == 0) {
            let remline = $(".checktoprighttop .checkrightline").last()
            if (remline.length) {
                vtotal -= remline.data("price")
                settotal(totaldiv,vtotal)
                remline.remove()
                if ($(".checktoprighttop .checkrightline").length == 0)
                    totaldiv.remove()
            }
            playsnd("beep")
        } else {
            $(".checklayertender").addClass("checkhide")
            $(".checklayersales").removeClass("checkhide")
            ttotal = 0
            cstate = 0
            tenderdiv.remove()
            changediv.remove()
            $(".checktoprightbottom").append(totaldiv)
            playsnd("beep")
        }
    }    
    updateprices()
}
function checkgo() {
    if (readysnd("beep")) {
        if (cstate == 0 && vtotal > 0) {
            $(".checklayersales").addClass("checkhide")
            $(".checklayertender").removeClass("checkhide")
            settotal(totaldiv,vtotal)
            $(".checktoprighttop").append(totaldiv)
            cstate = 1
            playsnd("beep")
        } else if (cstate == 1) {
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
            $(".checklayertender").addClass("checkhide")
            $(".checklayersales").removeClass("checkhide")
            vtotal = 0
            ttotal = 0
            cstate = 0
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
    }
    updateprices()
}
$(document).ready(function() {
    $(".checklayertender").addClass("checkhide");
    $(".checkitem").on("click",itemclick)
    $("#checkcancel").on("click",checkback)
    $("#checkgo").on("click",checkgo)
    updateprices()
})
