$("#game_type").change(function() {
    if ($("#game_type option:selected").text() == "Singles") {
	$(".second_player").removeClass("show_second_player").addClass("hide_second_player");
    } else {
	$(".second_player").removeClass("hide_second_player").addClass("show_second_player");
    }
});