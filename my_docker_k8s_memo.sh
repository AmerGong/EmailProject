docker build -t zhuangtao/message-au:latest .
docker push zhuangtao/message-au:latest  
docker rmi message-au
kubectl delete deployment message-au
kubectl delete service message-au
kubectl create deployment message-au --image=docker.io/zhuangtao/message-au:latest
kubectl expose deployment/message-au --type=NodePort --port 8080
kubectl get service

----------

export APPNAME=message
export USERNAME=zhuangtao
export NETNAME=NET_message

docker stop $APPNAME-ae $APPNAME-be $APPNAME-au $APPNAME-bu

docker rm $(docker ps -aq)

docker rmi $USERNAME/$APPNAME-ae:latest
docker rmi $USERNAME/$APPNAME-be:latest
docker rmi $USERNAME/$APPNAME-au:latest
docker rmi $USERNAME/$APPNAME-bu:latest

docker build -t $USERNAME/$APPNAME-ae:latest AE/
docker build -t $USERNAME/$APPNAME-be:latest BE/
docker build -t $USERNAME/$APPNAME-au:latest AU/
docker build -t $USERNAME/$APPNAME-bu:latest BU/

docker push $USERNAME/$APPNAME-ae:latest
docker push $USERNAME/$APPNAME-be:latest
docker push $USERNAME/$APPNAME-au:latest
docker push $USERNAME/$APPNAME-bu:latest

docker network create $NETNAME
docker run --network $NETNAME --name $APPNAME-ae -d $USERNAME/$APPNAME-ae:latest
docker run --network $NETNAME --name $APPNAME-be -d $USERNAME/$APPNAME-be:latest
docker run --network $NETNAME --name $APPNAME-au -p 5001:5001/tcp -d $USERNAME/$APPNAME-au:latest
docker run --network $NETNAME --name $APPNAME-bu -p 5000:5000/tcp -d $USERNAME/$APPNAME-bu:latest

#docker exec -it --user root $APPNAME-ae /bin/bash 

curl "http://localhost:5001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis%2020210439142018"
curl "http://localhost:5000/email?from=127.0.0.1:10079"
curl "http://localhost:5001/email?from=172.18.0.2:10080&to=172.18.0.3:10079&message=hi,nowis020210439142018"
curl "http://localhost:5000/email?from=172.18.0.3:10079"


curl "http://169.51.206.152:30001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis020210439142018"
curl "http://169.51.206.152:30000/email?from=127.0.0.1:10079"




