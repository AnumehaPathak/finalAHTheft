# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import re
import random
import requests
import pprint
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ImageModel
# Create your views here.

VERIFY_TOKEN='AntiHomeTheft'

PAGE_ACCESS_TOKEN='EAAKa0eCWBu4BAJjbRJv4TN3GeAd0KNKRTNHFcmJW6HZCuwDsSyatiDZBVVp8Wyz6n5ZAhEvZCohgFy4qMVUrzwxV8ZArn9v824r3uWLdwoJw112XbMhHBHfA0TvkVZBeXfgwu0ZAh2rrmkAUYgS9DK43ZBbnwKz4KhwdXJOURh93xAZDZD'


@method_decorator(csrf_exempt)
def getResponse(request):
    print request.POST
    print request.POST.__dict__
    # print request.FILES
    if request.method == "POST":
        image = request.FILES.get('media')
        if image is not None:
            id_user="1490578364307193"
            post_facebook_message(id_user,image,"hello")
        return HttpResponse("data received")
    else:
        return HttpResponse("request is not post")


def index(request):
    post_facebook_message("1531", "Hello")
    return HttpResponse('ok')


def post_facebook_message(fbid,image,text):
    # image = default_storage.save('image.jpg', ContentFile(image.read()))
    image = ImageModel(image=image)
    image.save()
    image=image.image.url
    image="https://antihta.herokuapp.com"+image
    print image
    import pdb;pdb.set_trace()
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg={
    "recipient":{
        "id":fbid
      },
      "message":{
        "attachment":{
          "type":"image",
          "payload":{
            "url":image
          }
        }
      }
    }       
    response_msg = json.dumps(response_msg)
    # response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":text}})
    # import pdb;pdb.set_trace()
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    



def find(title="girls"):
    url="http://api.tvmaze.com/singlesearch/shows?q=%s"%(title)
    resp = requests.get(url=url).text
    data = json.loads(resp)
    scoped_data=data["summary"]
    image_url=data["image"]["medium"]
    url_info=data['url']
    
    return scoped_data,image_url,url_info

class MyChatBotView(generic.View):
    def get(self,request,*args,**kwargs):
        if self.request.GET['hub.verify_token']==VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('oops invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self,request,*args,**kwargs):
        return generic.View.dispatch(self,request,*args,**kwargs)

    def post(self,request,*args,**kwargs):
        incoming_message=json.loads(self.request.body.decode('utf-8'))
        print incoming_message

        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_facebook_message(sender_id,message_text) 
                    
                except Exception as e:
                    print e
                    pass

        return HttpResponse() 
