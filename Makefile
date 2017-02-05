default: test

COMPOSE_FILE_DEV = docker-compose-dev.yml
COMPOSE_FILE_BUILD = docker-compose-build.yml

export OPAC_PROC_BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
export OPAC_PROC_VCS_REF=$(strip $(shell git rev-parse --short HEAD))
export OPAC_PROC_WEBAPP_VERSION=$(strip $(shell cat VERSION))

export OPAC_MONGODB_NAME=opac
export OPAC_MONGODB_HOST=$(strip $(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}' opac_opac_mongo_1))
export OPAC_MONGODB_PORT=27017

get_opac_mongo_info:
	@echo "OPAC_MONGODB_NAME " $(OPAC_MONGODB_NAME)
	@echo "OPAC_MONGODB_HOST " $(OPAC_MONGODB_HOST)
	@echo "OPAC_MONGODB_PORT " $(OPAC_MONGODB_PORT)

opac_proc_version:
	@echo "Version file: " $(OPAC_PROC_BUILD_DATE)

vcs_ref:
	@echo "Latest commit: " $(OPAC_PROC_VCS_REF)

build_date:
	@echo "Build date: " $(OPAC_PROC_WEBAPP_VERSION)

############################################
## atalhos docker-compose desenvolvimento ##
############################################

dev_compose_build:
	@docker-compose -f $(COMPOSE_FILE_DEV) build

dev_compose_up:
	@echo "OPAC_MONGODB_NAME " $(OPAC_MONGODB_NAME)
	@echo "OPAC_MONGODB_HOST " $(OPAC_MONGODB_HOST)
	@echo "OPAC_MONGODB_PORT " $(OPAC_MONGODB_PORT)
	@docker-compose -f $(COMPOSE_FILE_DEV) up -d

dev_compose_logs:
	@docker-compose -f $(COMPOSE_FILE_DEV) logs -f

dev_compose_stop:
	@docker-compose -f $(COMPOSE_FILE_DEV) stop

dev_compose_ps:
	@docker-compose -f $(COMPOSE_FILE_DEV) ps

dev_compose_rm:
	@docker-compose -f $(COMPOSE_FILE_DEV) rm -f

dev_compose_exec_shell_webapp:
	@docker-compose -f $(COMPOSE_FILE_DEV) exec webapp sh

# dev_compose_make_test:
# 	@docker-compose -f $(COMPOSE_FILE_DEV) exec webapp make test
