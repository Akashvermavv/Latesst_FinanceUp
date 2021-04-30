$(document).ready(function() {

$('#quantity').keyup(function(){
	$('#profit').val('');
	$('#amount').val('');

	var quantity=$('#quantity').val();

	var value=$('#value').val();
	var dailyprofit=$('#dailyprofit').val();


	$('#profit').val(dailyprofit*60*quantity-(value*quantity));
	$('#amount').val(value*quantity);


}); //quantity pressing function ends here

$(document).on('click','#buybutton',function(event){
	var quantity = $('#quantity').val();
	if(quantity == '' || quantity>200 ||quantity<0){
		alert('quantity is not valid');
		event.preventDefault();
	};

});//

})