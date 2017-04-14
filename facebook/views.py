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
# Create your views here.



VERIFY_TOKEN='AntiHomeTheft'

PAGE_ACCESS_TOKEN='EAAKa0eCWBu4BAJjbRJv4TN3GeAd0KNKRTNHFcmJW6HZCuwDsSyatiDZBVVp8Wyz6n5ZAhEvZCohgFy4qMVUrzwxV8ZArn9v824r3uWLdwoJw112XbMhHBHfA0TvkVZBeXfgwu0ZAh2rrmkAUYgS9DK43ZBbnwKz4KhwdXJOURh93xAZDZD'

def index(request):
    post_facebook_message("1531", "Hello")
    return HttpResponse('ok')


def post_facebook_message(fbid,message_text):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    text,image,url_info=find(message_text)
    if text is None:
        text="No show with such name "
    else:
        pass

    try:
        if len(text) > 315:
            text = text[3:315] + ' ...'
    except KeyError:
        text = ''

    response_msg_generic={
        "recipient":{
            "id":fbid 
          },
          "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements":[
                  {
                    "title":text,
                    "item_url":url_info,
                    "image_url":image,
                    "subtitle":"Nostalgia",
                    "buttons":[
                      {
                        "type":"web_url",
                        "url":url_info,
                        "title":"View Website"
                      },
                      {
                        "type":"postback",
                        "title":"Start Chatting",
                        "payload":"Another Show"
                      }              
                    ]
                  }
                ]
              }
            }
          }
    

    }
    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message_text}})
    #requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    response_msg_generic=json.dumps(response_msg_generic)

    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":text}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg_generic)
    #print status.json()
    

def handle_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    
    if payload=='Another Show':
        output_text='What other shows you want to know about ? '

    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":output_text}})
    status=requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
     







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
                    if 'postback' in message:
                        handle_postback(message['sender']['id'],message['postback']['payload'])
                    else:
                        pass
                except Exception as e:
                    print e
                #print message
                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_facebook_message(sender_id,message_text) 
                    
                except Exception as e:
                    print e
                    pass

        return HttpResponse() 
