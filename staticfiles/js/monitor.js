$("document").ready(()=>{
    $(".submit").click(()=>{
        $(".loader").css("display","block")
    });
    var uid = $("#userid").attr("data-id"); 
    console.log("monitor");

    $("#monitoring-items").empty();

    function loadMonitor(){
        $("#monitoring-items").empty();
        $.ajax({
            "url":"/monitor?uid="+uid,
            "method":'GET',
             success:function(resp){
                 console.log(resp)
                 let items = resp
                 if(items.length==0){
                     $("#monitoring-items").append("<h5 class='text-blue text-lighten-2'>No products are monitoring</h5>").html();
                 }
                 for(i=0;i<items.length;i++){
                     if(i==0){
                        $("#monitoring-items").append(`<tr class="orange">
                            <th>Product</th>
                            <th>Actual</th>
                            <th>Current</th>
                            <th>From</th>
                            <th>Buy</th>
                            <th>Remove</th>
                        </tr>`);
                     }
                      $("#monitoring-items").append(`<tr><td>${items[i].title}</td><td>₹${items[i].actual}</td><td>₹${items[i].current}</td><td>${items[i].site}</td><td><a class="btn orange lighten-3 text-white" target="_blank" href="${items[i].url}">Buy</a></td><td><button data-id="${items[i].id}" class="btn removeItem red lighten-2 text-white">Remove</button></td></tr>`).html();
                 }
                 $(".loader").css("display","none");
             }
        });
    }

    function addToMonitor(site,userid,title,price,url){
        $.ajax({
            url:`./addToMonitor?userid=${userid}&url=${url}&price=${price}&title=${title}&site=${site}`,
            method:"GET",
            success:function(resp){
                $(".added").remove();
                loadMonitor();
                $(".loader").css("display","none");
            }
        }).fail(()=>{
            $(".loader").css("display","none");
        });
    }

    $(".monitor-btn").click(function(e){
        $(".loader").css("display","block");
        let site = $(this).attr("data-site");
        let url = $(this).attr("data-url");
        let price = $(this).attr("data-price");
        let userid = $(this).attr("data-id");
        let title = $(this).attr("data-title");
        $(".monitor-btn").removeClass("added");
        $(this).addClass("added");
        addToMonitor(site,userid,title,price,url);
     });

     loadMonitor();

     $("body").on("click",".removeItem",function(){
       if(confirm("Do you want to remove monitoring?")){
        $(".loader").css("display","block");
        let id = $(this).attr("data-id");
        $.ajax({
            url:`/remove?id=${id}`,
            method:"GET",
            success:function(resp){
                loadMonitor();
                $(".loader").css("display","none");
            }
        }).fail(()=>{
           $(".loader").css("display","none");
        });
       }
});
});