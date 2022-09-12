
$(document).ready(()=>{
    let results = get_more_results();
});

function get_more_results(){
    let last_response_length = 0;

    $.ajax({
        url:"http://127.0.0.1:8000/stream",
        type:'get',
        data:{
            'q':'blockchain'
        },
        xhrFields:{
            onprogress:(data)=>{
                let response = data.target.response;
                let last_response_data = response.substring(last_response_length);
                // console.log(last_response_data)
                let json_data = JSON.parse(last_response_data);
                console.log(json_data)
                last_response_length = response.length;
            }
        }
    })
}
