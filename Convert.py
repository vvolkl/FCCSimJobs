import sys
import math
import ROOT as r

def layerID(x,y):
    R=math.sqrt(x**2+y**2)
    if   R<1950: return 1
    elif R<2000: return 2
    elif R<2100: return 3
    elif R<2200: return 4
    elif R<2300: return 5
    elif R<2400: return 6
    elif R<2500: return 7
    elif R<2540: return 8

    elif R<2950: return 9
    elif R<3100: return 10
    elif R<3200: return 11
    elif R<3400: return 12
    elif R<3500: return 13
    elif R<3600: return 14
    elif R<3800: return 15
    elif R<4100: return 16
    elif R<4400: return 17
    elif R<4600: return 18
    else : return 99999
    
def signy(y):
    if y>0: return 1
    elif y<0: return -1
    return 0

if len(sys.argv)!=3:
    print 'usage python Convert.py infile outfile'
infile_name = sys.argv[1]
outfile_name = sys.argv[2]

infile=r.TFile.Open(infile_name)
intree=infile.Get('events')

gen_eta = r.std.vector(float)()
gen_phi = r.std.vector(float)()
gen_pt  = r.std.vector(float)()
gen_energy = r.std.vector(float)()
gen_pdgid = r.std.vector(float)()
gen_status = r.std.vector(float)()

rec_eta = r.std.vector(float)()
rec_phi = r.std.vector(float)()
rec_pt  = r.std.vector(float)()
rec_ene = r.std.vector(float)()
rec_x = r.std.vector(float)()
rec_y = r.std.vector(float)()
rec_z = r.std.vector(float)()
rec_layer = r.std.vector(int)()

outfile=r.TFile(outfile_name,"recreate")
outfile.mkdir('ana')
r.gDirectory.cd('ana')
outtree=r.TTree('hgc','hgc')

outtree.Branch("rechit_pt", rec_pt)
outtree.Branch("rechit_eta", rec_eta)
outtree.Branch("rechit_phi", rec_phi)
outtree.Branch("rechit_energy", rec_ene)
outtree.Branch("rechit_layer", rec_layer)
outtree.Branch("rechit_x", rec_x)
outtree.Branch("rechit_y", rec_y)
outtree.Branch("rechit_z", rec_z)

outtree.Branch("gen_pt", gen_pt)
outtree.Branch("gen_eta", gen_eta)
outtree.Branch("gen_phi", gen_phi)
outtree.Branch("gen_energy", gen_energy)
outtree.Branch("gen_status", gen_status)
outtree.Branch("gen_pdgid", gen_pdgid)

for event in intree:
    for g in event.allGenParticles:
        position = r.TVector3(g.core.p4.px,g.core.p4.py,g.core.p4.pz)

        pt=math.sqrt(g.core.p4.px**2+g.core.p4.py**2)
        eta=position.Eta()
        phi=position.Phi()

        tlv=r.TLorentzVector()
        tlv.SetPtEtaPhiM(pt,eta,phi,g.core.p4.mass)
        gen_pt.push_back(pt)
        gen_eta.push_back(eta)
        gen_phi.push_back(phi)
        gen_energy.push_back(math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2))

        if math.fabs(tlv.E()-math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2))>0.01 and g.core.status==1:
            print '=======================etlv  ',tlv.E(),'    ',math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2),'  eta  ',eta,'   phi   ',phi,'  x  ',g.core.p4.px,'  y  ',g.core.p4.py,'  z  ',g.core.p4.pz
        #if g.core.status==1:
            #print 'etlv  ',tlv.E(),'    ',math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2),'  eta  ',eta,'   phi   ',phi,'  x  ',g.core.p4.px,'  y  ',g.core.p4.py,'  z  ',g.core.p4.pz
        gen_pdgid.push_back(g.core.pdgId)
        gen_status.push_back(g.core.status)

    for c in event.cellHCalPositions:
        position = r.TVector3(c.position.x,c.position.y,c.position.z)
        rec_ene.push_back(c.core.energy)
        rec_eta.push_back(position.Eta())
        rec_phi.push_back(position.Phi())
        rec_pt.push_back(c.core.energy*position.Unit().Perp())
        rec_layer.push_back(layerID(c.position.x,c.position.y))
        rec_x.push_back(c.position.x/10.)
        rec_y.push_back(c.position.y/10.)
        rec_z.push_back(c.position.z/10.)
        #print '  new eta HCAL  ',position.Eta(), ' pt  ',c.core.energy*position.Unit().Perp()
        
    for c in event.cellECalPositions:
        position = r.TVector3(c.position.x,c.position.y,c.position.z)
        rec_ene.push_back(c.core.energy)
        rec_eta.push_back(position.Eta())
        rec_phi.push_back(position.Phi())
        rec_pt.push_back(c.core.energy*position.Unit().Perp())
        rec_layer.push_back(layerID(c.position.x,c.position.y))
        rec_x.push_back(c.position.x/10.)
        rec_y.push_back(c.position.y/10.)
        rec_z.push_back(c.position.z/10.)
        #print '  new eta  ECLA  ',position.Eta(), ' pt  ',c.core.energy*position.Unit().Perp()
    
    for c in event.cellExtHCalPositions:
        position = r.TVector3(c.position.x,c.position.y,c.position.z)
        rec_ene.push_back(c.core.energy)
        rec_eta.push_back(position.Eta())
        rec_phi.push_back(position.Phi())
        rec_pt.push_back(c.core.energy*position.Unit().Perp())
        rec_layer.push_back(layerID(c.position.x,c.position.y))
        rec_x.push_back(c.position.x/10.)
        rec_y.push_back(c.position.y/10.)
        rec_z.push_back(c.position.z/10.)
        #print '  new eta  extHCal  ',position.Eta(), ' pt  ',c.core.energy*position.Unit().Perp()


    outtree.Fill()
    gen_eta.clear()
    gen_phi.clear()
    gen_pt.clear()
    gen_energy.clear()
    gen_pdgid.clear()
    gen_status.clear()

    rec_eta.clear()
    rec_phi.clear()
    rec_pt.clear()
    rec_ene.clear()
    rec_layer.clear()
    rec_x.clear()
    rec_y.clear()
    rec_z.clear()
outtree.Write()
outfile.Write()
outfile.Close()


