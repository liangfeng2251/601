#!/bin/bash
# Created by HM on 2023-07-08

container="qy-mss-q-backend"
outer_port=13010
inside_port=12008
image_name="qy/mss-q-backend"
image_version="1.0.0"
container_id=$(docker ps --filter name=${container} -q)

if [ "$container_id" ]
then
	echo "容器运行中：ID $container_id 名 $container"
	docker stop "$container_id"
else
	echo "容器没有运行"
	container_id=$(docker ps -a --filter name=${container} -q)
fi

if [ "$container_id" ]
then
	echo "容器删除中..."
	docker rm "$container_id"
else
	echo "容器不存在"
fi

echo "旧镜像ID获取"
image_id=$(docker images | awk '/qy\/mss-q-backend/ { print $3 }')
echo "$image_id"
echo "构建镜像中..."
docker build -t $image_name:$image_version .
echo "构建完成"

sleep 1

echo "启动容器中..."
docker run --name $container -p $outer_port:$inside_port -d $image_name:$image_version
echo "启动完成"

if [ "$image_id" ];
then
    echo "旧镜像删除中..."
    docker rmi "$image_id"
else
  echo "旧镜像不存在"
fi

sleep 1

echo "SUCCESS"
date +"%Y-%m-%d %H:%M:%S"
