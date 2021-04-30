/*-----------------------------------------------------------------------------------*/
/*	Start Revolution Slider
/*-----------------------------------------------------------------------------------*/

	jQuery(document).ready(function() {		
		revapi = jQuery("#rev_slider").revolution({
			sliderType:"standard",
			jsFileLocation:"../style/rs-plugin/js/",
			dottedOverlay:"none",
			delay:9000,
			navigation: {
				arrows:{enable:true,style:"metis"}				
			},		
			parallax: {
				type:"mouse",
				origo:"slidercenter",
				speed:2000,
				levels:[2,3,4,5,6,7,10,11,12,13],
			},			
			responsiveLevels:[1240,1024,778,480],
			gridwidth:[1240,1024,778,480],
			gridheight:[580,480,580,480],
		});		
	});	/*ready*/
	
	jQuery(document).ready(function() {		
		revapi = jQuery("#rev_slider_fixed").revolution({
			sliderType:"standard",
			jsFileLocation:"../style/rs-plugin/js/",
			sliderLayout:"fullwidth",
			dottedOverlay:"none",
			delay:9000,
			parallax: {
				type:"mouse",
				origo:"slidercenter",
				speed:2000,
				levels:[1,2,3,4,5,6,7,10,11,12,13],
			},			
			responsiveLevels:[1240,1024,778,480],
			gridwidth:[1240,1024,778,480],
			gridheight:[580,480,580,480],
		});		
	});	/*ready*/
	
	jQuery(document).ready(function() {		
		revapi = jQuery("#rev_slider_100_1").revolution({
			sliderType:"standard",
			jsFileLocation:"../../revolution/js/",
			sliderLayout:"fullwidth",
			dottedOverlay:"none",
			delay:9000,
			responsiveLevels:[1240,1024,778,480],
			gridwidth:[1240,1024,778,480],
			gridheight:[620,768,960,720],
			lazyType:"none",
			parallax: {
				type:"mouse",
				origo:"slidercenter",
				speed:2000,
				levels:[2,3,4,5,6,7,12,16,10,50],
				disable_onmobile:"on"
			},
			shadow:0,
			spinner:"off",
			stopLoop:"on",
			stopAfterLoops:0,
			stopAtSlide:1,
			shuffle:"off",
			autoHeight:"on",
			fullScreenAlignForce:"off",
			fullScreenOffsetContainer: "",
			fullScreenOffset: "60px",
			disableProgressBar:"on",
			hideThumbsOnMobile:"off",
			hideSliderAtLimit:0,
			hideCaptionAtLimit:0,
			hideAllCaptionAtLilmit:0,
			debugMode:false,
			fallbacks: {
				simplifyAll:"off",
				disableFocusListener:false,
			}
		});	});	/*ready*/
	
	
	jQuery(document).ready(function() {		
		revapi = jQuery("#rev_slider_banner").revolution({
			sliderType:"standard",
			jsFileLocation:"../../revolution/js/",
			sliderLayout:"fullscreen",
			dottedOverlay:"none",
			delay:9000,
			responsiveLevels:[1240,1024,778,480],
			gridwidth:[1240,1024,778,480],
			gridheight:[868,768,960,720],
			lazyType:"none",
			shadow:0,
			spinner:"off",
			stopLoop:"on",
			stopAfterLoops:0,
			stopAtSlide:1,
			shuffle:"off",
			autoHeight:"off",
			fullScreenAlignForce:"off",
			fullScreenOffsetContainer: "",
			fullScreenOffset: "",
			disableProgressBar:"on",
			hideThumbsOnMobile:"off",
			hideSliderAtLimit:0,
			hideCaptionAtLimit:0,
			hideAllCaptionAtLilmit:0,
			debugMode:false,
			fallbacks: {
				simplifyAll:"off",
				nextSlideOnWindowFocus:"off",
				disableFocusListener:false,
			}
		});		
	});	/*ready*/

/*-----------------------------------------------------------------------------------*/
/*	End Revolution Slider
/*-----------------------------------------------------------------------------------*/




