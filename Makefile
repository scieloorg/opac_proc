default: test

COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_BUILD = docker-compose-build.yml

export OPAC_PROC_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
export OPAC_PROC_VCS_REF=$(strip $(shell git rev-parse --short HEAD))
export OPAC_PROC_WEBAPP_VERSION=$(strip $(shell cat VERSION))

ifndef OPAC_MONGODB_HOST
	export OPAC_MONGODB_NAME=opac
	export OPAC_MONGODB_HOST=$(strip $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' opac_opac_mongo_1))
	export OPAC_MONGODB_PORT=27017
else
	@echo "$$OPAC_MONGODB_HOST já foi definida previamente"
endif

ifndef OPAC_GRPC_HOST
	export OPAC_GRPC_HOST=$(strip $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' opacssm_grpc_1))
	export OPAC_GRPC_PORT=5000
else
	@echo "$$OPAC_MONGODB_HOST já foi definida previamente"
endif

get_opac_mongo_info:
	@echo "***************************************"
	@echo "* OPAC_MONGODB_NAME: \t" $(OPAC_MONGODB_NAME)
	@echo "* OPAC_MONGODB_HOST: \t" $(OPAC_MONGODB_HOST)
	@echo "* OPAC_MONGODB_PORT: \t" $(OPAC_MONGODB_PORT)
	@echo "***************************************"

get_opac_grpc_info:
	@echo "***************************************"
	@echo "* OPAC_GRPC_HOST: \t" $(OPAC_GRPC_HOST)
	@echo "* OPAC_GRPC_PORT: \t" $(OPAC_GRPC_PORT)
	@echo "***************************************"

opac_proc_version:
	@echo "Version file: " $(OPAC_PROC_BUILD_DATE)

vcs_ref:
	@echo "Latest commit: " $(OPAC_PROC_VCS_REF)

build_date:
	@echo "Build date: " $(OPAC_PROC_WEBAPP_VERSION)

get_build_info:
	@echo "Version file: " $(OPAC_PROC_BUILD_DATE)
	@echo "Latest commit: " $(OPAC_PROC_VCS_REF)
	@echo "Build date: " $(OPAC_PROC_WEBAPP_VERSION)


############################################
## atalhos docker-compose desenvolvimento ##
############################################

dev_compose_build: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_compose_up: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_compose_logs: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f $1

dev_compose_stop: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_compose_ps: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_compose_rm: get_opac_mongo_info get_opac_grpc_info
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f $<

dev_compose_exec_shell_webapp: dev_compose_up
	@docker-compose -f $(COMPOSE_FILE_DEV) exec webapp sh

dev_compose_make_test: dev_compose_up
	@docker-compose -f $(COMPOSE_FILE_DEV) exec webapp python opac_proc/manage.py test

dev_compose_scale_workers: dev_compose_up
	@docker-compose -f $(COMPOSE_FILE_DEV) scale rq-worker=4

test:
	@python opac_proc/manage.py test

dev_create_superuser:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec webapp make create_superuser

create_superuser:
	@python opac_proc/manage.py create_superuser

#####################################################
## atalhos docker-compose build e testes no traivs ##
#####################################################

travis_compose_build: get_opac_mongo_info get_build_info
	@docker-compose -f $(COMPOSE_FILE_BUILD) build

travis_compose_up: get_opac_mongo_info get_build_info
	@docker-compose -f $(COMPOSE_FILE_BUILD) up -d

travis_compose_make_test: get_opac_mongo_info get_build_info
	@docker-compose -f $(COMPOSE_FILE_BUILD) exec webapp python opac_proc/manage.py test

travis_compose_exec_shell_webapp: travis_compose_up
	@docker-compose -f $(COMPOSE_FILE_BUILD) exec webapp sh

travis_run_audit:
	@docker run \
	-it --net host --pid host \
	--cap-add audit_control \
	-v /var/lib:/var/lib \
  	-v /var/run/docker.sock:/var/run/docker.sock \
  	-v /usr/lib/systemd:/usr/lib/systemd \
  	-v /etc:/etc \
  	--label docker_bench_security \
	docker/docker-bench-security

travis_create_opac_mongodb_container:
	@docker run \
	--user mongodb \
	--name opac_opac_mongo_1 \
	--restart always \
	--hostname opac-mongo \
	-p 27017:27017 \
	-v /etc/localtime:/etc/localtime:ro \
	-d \
	mongo:latest


###########################################################
## atalhos docker-compose build e push para o Docker Hub ##
###########################################################

release_docker_build: get_opac_mongo_info get_build_info
	@echo "[Building] Image full tag: $(TRAVIS_REPO_SLUG):$(COMMIT)"
	@docker build \
	-t $(TRAVIS_REPO_SLUG):$(COMMIT) \
	--build-arg OPAC_PROC_BUILD_DATE=$(OPAC_PROC_BUILD_DATE) \
	--build-arg OPAC_PROC_VCS_REF=$(OPAC_PROC_VCS_REF) \
	--build-arg OPAC_PROC_WEBAPP_VERSION=$(OPAC_PROC_WEBAPP_VERSION) .

release_docker_tag: get_opac_mongo_info get_build_info
	@echo "[Tagging] Target image -> $(TRAVIS_REPO_SLUG):$(COMMIT)"
	@echo "[Tagging] Image name:latest -> $(TRAVIS_REPO_SLUG):latest"
	@docker tag $(TRAVIS_REPO_SLUG):$(COMMIT) $(TRAVIS_REPO_SLUG):latest
	@echo "[Tagging] Image name:latest -> $(TRAVIS_REPO_SLUG):travis-$(TRAVIS_BUILD_NUMBER)"
	@docker tag $(TRAVIS_REPO_SLUG):$(COMMIT) $(TRAVIS_REPO_SLUG):travis-$(TRAVIS_BUILD_NUMBER)

release_docker_push: get_opac_mongo_info get_build_info
	@echo "[Pushing] pushing image: $(TRAVIS_REPO_SLUG)"
	@docker push $(TRAVIS_REPO_SLUG)
	@echo "[Pushing] push $(TRAVIS_REPO_SLUG) done!"
