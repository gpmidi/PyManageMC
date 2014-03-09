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


def generateTemplate(opts):
    log.debug("Going to generate template")
    kws = {
            'os':opts.os,
            'project':opts.project,
            'releaseType':opts.releaseType,
            'projectVersionStr':opts.projectVersionStr,
            'templatePath':opts.templatePath,
            'cfgsPath':opts.cfgsPath,
            'tagPrefix':opts.tagPrefix,
            }
    templateListing = os.listdir(opts.templatePath)
    names = [
             ('Base',),
             ("%s" % opts.os,),
             ('%s_%s' % (opts.project, opts.os),),
             ('%s_%s_%s' % (opts.releaseType, opts.project, opts.os),),
             ('%s_%s' % (opts.projectVersionStr, opts.os),),
             ]
    found = None
    for s in names:
        m = "%s.Dockerfile.template" % s[0]
        if s in templateListing:
            found = s
    if found is None:
        raise ValueError("Expected to find a valid template")
    kw['templateName'] = found[0]
    outFile = os.path.join(
                           ops.cfgsPath,
                           found[0].replace('.template', ''),
                           )
    rendered = render_to_string(templateName, kw)
    log.info("Writing template to %r", outFile)
    with open(outFile, 'w') as f:
        f.write(rendered)
    log.debug("Done generating template")


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

    generateTemplate(opts = opts)

    log.info("Done")
