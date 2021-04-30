/*-----------------------------------------------------------------------------------*/
/*	Start instagram
/*-----------------------------------------------------------------------------------*/

$(document).ready(function() { 
	var imgs = [];
		var userFeed = new Instafeed({
		get: 'user',
		userId: 1357647689,
		accessToken: '1357647689.1677ed0.dc0de00cb515414db7a06cc416c987a1',
        limit: 8,
		tagName: 'play',
		resolution: 'standard_resolution',  
        template: '<li><a href="{{link}}" target="_blank"><img src="{{image}}" /></a></li>',
        success: function (data) {
            // read the feed data and create owr own dat3193855a struture.
            var images = data.data;
            var result;
            for (i = 0; i < images.length; i++) {
                var image = images[i];
                result = this._makeTemplate(this.options.template, {
                    model: image,
                    id: image.id,
                    link: image.link,
                    image: image.images[this.options.resolution].url
                });
                imgs.push(result);
            }
            //split the feed into divs
            $("#instafeed2").html(imgs.slice(0, 8));
        }
    });
    userFeed.run();	
});	

/*-----------------------------------------------------------------------------------*/
/*	End instagram
/*-----------------------------------------------------------------------------------*/

