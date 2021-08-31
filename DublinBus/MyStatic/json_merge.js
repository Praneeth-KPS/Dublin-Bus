var jsonStr = '{"theTeam":[{"teamId":"1","status":"pending"},{"teamId":"2","status":"member"},{"teamId":"3","status":"member"}]}';

var obj = JSON.parse(jsonStr);
obj['theTeam'].push({"teamId":"4","status":"pending"});
jsonStr = JSON.stringify(obj);
//