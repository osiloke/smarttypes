
var global_reduction_id = -1;
var global_num_groups = -1;
var global_old_group_index = -1;
var global_old_group_color = "";
var global_old_node_id = "";
var global_old_node_color = "";
var global_old_following = [];


var load_social_map = function(reduction_id, num_groups){

    global_reduction_id = reduction_id;
    global_num_groups = num_groups;

    reduction_href = '/social_map/map_data.json?reduction_id='+reduction_id;
    d3.json(reduction_href, function(data){

        var coord_scale = d3.scale.linear().domain(
            [data.min_coord,data.max_coord])
            .range([10,420]);

        var color_scale = d3.scale.linear().domain([-1,num_groups])
            .interpolate(d3.interpolateRgb)
            .range(["#cccccc", "#000000"]);
        
        $('#map_data').html('');
        var svg = d3.select("#map_data").append("svg")
            .attr("width", 430)
            .attr("height", 430);

        svg.selectAll("circle")
            .data(data.coordinates)
            .enter().append("circle")
            .attr("id", function(d, i) { return "id_" + d.id; })
            .attr("class", function(d, i) { return "group_" + d.group_index; })
            .attr("cx", function(d, i) { return coord_scale(d.x); })
            .attr("cy", function(d, i) { return coord_scale(d.y); })
            .attr("r", 3)
            .style("fill", function(d, i) { return color_scale(d.group_index); })
            .style("cursor", "pointer")
            .on("click", function(d,i) { 
                if (d.group_index < 0){
                    show_node(d.id, reduction_id);
                }
                else{
                    show_cluster(d.group_index, reduction_id);
                }
            });
        
        $('div#spinner').hide();
        global_old_group_index = -1;
        global_old_group_color = "";
        show_cluster(0, reduction_id);
        global_old_node_id = "";
        global_old_node_color = "";
        show_node("", reduction_id);

    });
}

var show_node = function(node_id, reduction_id){

    //change old group color back
    if (global_old_group_index != -1){
        d3.selectAll('circle.group_' + global_old_group_index).style("fill", global_old_group_color);
    }
    global_old_group_index = -1;
    global_old_group_color = "";

    //change following color back
    global_old_following.forEach(function(following_id){ 
        d3.selectAll('#id_' + following_id).style("fill", global_old_node_color);
    });

    //change old node color back
    if (global_old_node_id != ""){
        d3.selectAll('#id_' + global_old_node_id).style("fill", global_old_node_color);
    }
    global_old_node_id = node_id;
    global_old_node_color = d3.selectAll('#id_' + node_id).style("fill");

    //highlight selected node
    d3.selectAll('#id_' + node_id).style("fill", '#00FF00');
    $('#current_group').html("");

    $.ajax({type:"POST",
            url:"/social_map/node_details",
            cache:false,
            data:{'node_id': node_id, 'reduction_id':reduction_id},
            dataType:"html",
            error:function(){},
            success:function(html){
                $('#group_details').html('');
                $('#group_details').html(html);
                bind_highlight_following_click();
            }
    });
};

var show_cluster = function(group_idx, reduction_id){

    //node not tied to a group
    if (group_idx < 0){
        return
    }

    //change the old color back
    if (global_old_group_index != -1){
        d3.selectAll('circle.group_' + global_old_group_index).style("fill", global_old_group_color);
    }
    global_old_group_index = group_idx;
    global_old_group_color = d3.selectAll('circle.group_' + group_idx).style("fill");
    d3.selectAll('circle.group_' + group_idx).style("fill", '#00FF00');

    if (global_old_node_id != ""){
        d3.selectAll('#id_' + global_old_node_id).style("fill", global_old_node_color);
    }
    global_old_node_id = "";
    global_old_node_color = "";

    $('#current_group').html(group_idx + 1);
    $.ajax({type:"POST",
            url:"/social_map/group_details",
            cache:false,
            data:{'group_index': group_idx, 'reduction_id':reduction_id},
            dataType:"html",
            error:function(){},
            success:function(html){
                $('#group_details').html('');
                $('#group_details').html(html);
                d3.selectAll("li.twitter_user").style("background-color", 
                    function(d, i) { return i % 2 ? "#fff" : "#eee"; });
            }
    });
};

var load_next_or_previous_reduction = function(reduction_id, next_or_previous){

    $.ajax({type:"GET",
            url:"/social_map/next_or_previous_reduction_id",
            cache:false,
            data:{'reduction_id':reduction_id, 'next_or_previous':next_or_previous},
            dataType:"json",
            error:function(){},
            success:function(data){
                load_social_map(data.reduction_id, data.num_groups);
                bind_next_or_prev_reduction_click();
            }
    });

};

var bind_next_or_prev_reduction_click = function(){
    $('a.next_or_prev_reduction').unbind().click(function(){
        load_next_or_previous_reduction(global_reduction_id, 
            $(this).attr('id'));
        return false;
    });
};

var bind_root_user_selector_change = function(){
    $("select#root_user_selector").unbind().change(function(){
        var user_id = $("select#root_user_selector option:selected").val();
        window.location = '/social_map?user_id=' + user_id;
    });
};

var bind_highlight_following_click = function(){
    $("a.highlight_following").unbind().click(function(){

        global_old_following = $.parseJSON($(this).attr('data-following'));
        global_old_following.forEach(function(following_id){ 
            d3.selectAll('#id_' + following_id).style("fill", '#FF0000');
        });
        return false;

    });
};




