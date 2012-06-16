#!/usr/bin/env make -rRf

##    {filename} - {description}
##
{prepend:##
{reparse:{include:{conf_dir}/{license}}}}

$(info I'm a makefile: ${{MAKEFILE_LIST}})
