.DEFAULT_GOAL = default
%:: ; ${MAKE} -C .. $(notdir $(shell pwd))/$@
