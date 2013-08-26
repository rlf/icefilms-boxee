/** 
 * CoffeeScript doesn't support web-workers - yet
 **/
self.addEventListener('message', function(event) {
	var offset = 0;
	var count = 100;
	var url = 'http://lockfuglsang.dk/boxee/icerss/icefilms.php?url=' + event.data;
	
	while (offset < count) {
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url + "&offset=" + offset + "&count=12", false);
		xhr.onreadystatechange = function () {
			if (xhr.readyState == 4) {
				if (xhr.status == 200) {
					var data = eval('(' + xhr.responseText + ')');
					if (data.success) {
						count = data.data['count'];
						offset += data.data['movies'].length;
					} else {
						offset = count;
					}
					self.postMessage(data);
				} else {
					self.postMessage({'status' : false, 'data' :[], 'message' : 'ERROR: ' + xhr.status});
				}
			}
		}
		xhr.send();
	}	
	self.close();
});
  
