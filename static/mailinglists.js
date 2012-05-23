$(function() {
  $("#moar_lists").click(function() {
    var tr_clone = $(".ml_field").last().closest("tr").clone();

    // Fix the <tr>'s id -- yeah this is ugly.
    tr_clone.attr("id", tr_clone.attr("id").replace(tr_clone.attr("id").split("-")[1], parseInt(tr_clone.attr("id").split("-")[1])+1));

    // Fix the label's "for".
    var label = tr_clone.find("label").first();
    label.attr("for", label.attr("for").replace(label.attr("for").split("-")[1], parseInt(label.attr("for").split("-")[1])+1));

    // Fix the field's id and name.
    var field = tr_clone.find("input[type=text]").first();
    field.attr("id", field.attr("id").replace(field.attr("id").split("-")[1], parseInt(field.attr("id").split("-")[1])+1));
    field.attr("name", field.attr("name").replace(field.attr("name").split("-")[1], parseInt(field.attr("name").split("-")[1])+1));
    field.val("");

    // Add all the work we did to the form.
    $("#tr_moar_lists").before(tr_clone);
    
  });
});