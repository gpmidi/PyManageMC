#!/usr/bin/python
""" Generate Dockerfiles
"""
import logging
log = logging.getLogger("PyManageMC.docker.generate")

# Builtin
from optparse import OptionParser
import os,os.path,sys

# External
from django.conf import settings
from django.template.loader import render_to_string

# Ours

def createSettings(opts):
    assert opts.templatePath, 'No template path defined!'
    settings.configure(DEBUG = True, TEMPLATE_DEBUG = True,
        TEMPLATE_DIRS = (ops.templatePath,))


def generateAllTemplates(opts):
    log.debug("Generating all template files")
    for fil in os.listdir(opts.templatePath):
        log.debug("Found file %r",fil)
        if str(fil).endswith('.template'):
            generateTemplate(opts=opts,templatePath=fil)
    log.debug("Done generating templates")

def generateTemplate(opts, **kw):
    templatePath = kw.get('templatePath', None)
    log.debug("Going to generate template %r", templatePath)
    templateName = os.path.relpath(path = templatePath, start = opts.templatePath)
    for k, v in {
            'os':opts.os,
            'project':opts.project,
            'releaseType':opts.releaseType,
            'projectVersionStr':opts.projectVersionStr,
            'templatePath':opts.templatePath,
            'cfgsPath':opts.cfgsPath,
            'templateName':templateName,
            'tagPrefix':opts.tagPrefix,
            }:
        if k not in kw:
            kw[k] = v
    outFile = os.path.join(
                           ops.cfgsPath,
                           os.path.basename(templateName).replace('.template', ''),
                           )
    rendered = render_to_string(templateName, kw)

    log.debug("Done generating template %r", templatePath)


if __name__ == "__main__":
    log.info("Starting")

    parser = OptionParser()
    parser.add_option(
                      "--os",
                      dest = "os",
                      action = 'store',
                      type = str,
                      default = None,
                      help = "GuestOS [default %default]",
                      )
    parser.add_option(
                      "--project",
                      dest = "project",
                      action = 'store',
                      type = str,
                      default = "vanilla",
                      help = "MinecraftProject [default %default]",
                      )
    parser.add_option(
                      "--releaseType",
                      dest = "releaseType",
                      action = 'store',
                      type = str,
                      default = "stable",
                      help = "MinecraftReleaseType [default %default]",
                      )
    parser.add_option(
                      "--projectVersionStr",
                      dest = "projectVersionStr",
                      action = 'store',
                      type = str,
                      default = None,
                      help = "MinecraftProjectVersion [default %default]",
                      )
    parser.add_option(
                      "--templatePath",
                      dest = "templatePath",
                      action = 'store',
                      type = str,
                      default = None,
                      help = "Location of the Dockerfile templates [default %default]",
                      )
    parser.add_option(
                      "--cfgsPath",
                      dest = "cfgsPath",
                      action = 'store',
                      type = str,
                      default = None,
                      help = "Location to store the generated Dockerfiles. [default %default]",
                      )
    parser.add_option(
                      "--tagPrefix",
                      dest = "tagPrefix",
                      action = 'store',
                      type = str,
                      default = '',
                      help = "Prefix to use for all generated tag names. [default %default]",
                      )
    parser.add_option(
                      "--verbose",
                      dest = "verbose",
                      action = 'store_true',
                      type = boolean,
                      default = False,
                      help = "Verbose logging [default %default]",
                      )

    (opts, args) = parser.parse_args()
    if opts.verbose:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.INFO)
    log.debug("Logging setup")

    createSettings(opts = opts)



    log.info("Done")
