$(document).ready(function(){

	$(document).on('click','#withdraw_submit',function(){

		via=$('.btn-select').val();
		amount=$('#amount').val();
		password=$('#password').val();

		if (via=='' || amount=='' || password==''){
			alert('all fields are required');
		}else{
			$('#withdraw_submit').text('loading......');


			$.ajax({
				dataType:'json',
				type:'GET',
				data:{via:via,amount:amount,password:password},
				url:'/dashboard/withdraw_request_premium/'
			})

			.done(function(data){

				var message=data.message;
				$('#messagebox').empty();
				$('#messagebox').append('<div class="alert alert-info">'+message+'</div');
				$('#withdraw_submit').text('withdraw');
			})

			.fail(function(){
				$('#messagebox').empty();
				$('#messagebox').append('<div class="alert alert-danger">something went wrong</div');

			});








		};








	});







})
