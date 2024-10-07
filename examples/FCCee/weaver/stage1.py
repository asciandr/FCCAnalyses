from examples.FCCee.weaver.config import (
    variables_pfcand,
    variables_jet,
    variables_event,
)

from addons.ONNXRuntime.jetFlavourHelper import JetFlavourHelper
from addons.FastJet.jetClusteringHelper import ExclusiveJetClusteringHelper

jetFlavourHelper = None
jetClusteringHelper = None

# Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis:
    # __________________________________________________________
    # Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        global jetClusteringHelper
        global jetFlavourHelper

        from examples.FCCee.weaver.config import collections, njets

        ## ANDREA: define index collections of reco'ed and truth MC particles
        df = df.Alias("MCRecoAssociations0ind", "MCRecoAssociations#0.index")
        df = df.Alias("MCRecoAssociations1ind", "MCRecoAssociations#1.index")
        #df = df.Alias("Jet0", "Jet#3.index")
        df = df.Alias("Jet0", "Jet")


        ## define jet clustering parameters
        ## ANDREAL try to filter out photons below 2 GeV -> impact on (gluon) tagging?
        jetClusteringHelper = ExclusiveJetClusteringHelper(collections["PFParticles"], njets)
#        df = (
#            df
#            .Alias("selected_pfcand","ReconstructedParticles")
#            .Define("selected_pfcand_p","ReconstructedParticle::get_p(selected_pfcand)")
#            .Define("selected_pfcand_type","ReconstructedParticle::get_type(selected_pfcand)")
#	    .Filter("(selected_pfcand_type==22 && selected_pfcand_p>2.) || selected_pfcand_p>0.")
#        )
#        jetClusteringHelper = ExclusiveJetClusteringHelper("ReconstructedParticles", njets)

        ## run jet clustering
        df = jetClusteringHelper.define(df)

        ## define jet flavour tagging parameters
        jetFlavourHelper = JetFlavourHelper(
            collections,
            jetClusteringHelper.jets,
            jetClusteringHelper.constituents,
        )

        ## define observables for tagger
        df = jetFlavourHelper.define(df)

        ## compute invariant mass of two leading jets
        df = df.Define("jet_p4", "JetConstituentsUtils::compute_tlv_jets({})".format(jetClusteringHelper.jets))
        df = df.Define("event_invariant_mass", "JetConstituentsUtils::InvariantMass(jet_p4[0], jet_p4[1])")

        return df

    # __________________________________________________________
    # Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branches_pfcand = list(variables_pfcand.keys())
        branches_jet = list(variables_jet.keys())
        branches_event = list(variables_event.keys())

        branchList = branches_event + branches_jet + branches_pfcand

        return branchList
