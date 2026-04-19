This repository contains a prototype of a USD Asset Browser currently in development.

It is designed for managing USD assets, with folder structure validation and import into a production pipeline.

Imported libraries can then be brought into a USD stage across different DCCs. In this example, I’m using Houdini, and in standalone mode it simply opens files in usdview.

The asset check includes validation, which is still in development—currently it only checks folder structure and USD files against the expected naming convention.

When importing a library, the tool creates a temporary stage, references the asset, procedurally sets up a render camera based on its size, adds a light rig, and generates a thumbnail.

If validation fails, there’s an option to adjust the asset folder structure. Editing is fairly basic for now, but I’m planning to extend it.

Current features
- Asset validation against the expected production pipeline folder structure (basic example; to be extended)
- Thumbnail rendering
- Houdini integration with asset import
- Asset preview in usdview when running in standalone mode
- Basic asset editing (to be extended)

All rendering and folder structure configurations are defined in `config.py`.

A short demo showcasing the current state of development is included below.

https://github.com/user-attachments/assets/eb0cb7b3-b052-468e-a7a9-a993532e1b8e

---

One of the core features—now merged into the main branch—is an asset check-in workflow. As an example, the project uses a KitBash-style asset library.

The check-in process includes:
- Creating a library metadata catalog
- Generating a temporary USD stage for each asset
- Adding a light rig
- Computing camera position and rotation based on the asset’s bounding box for thumbnail framing
- Rendering thumbnails
  
---

Example rendered thumbnails:

<img width="256" height="256" alt="KB3D_IRF_BldgLgFortress_A" src="https://github.com/user-attachments/assets/14e2b59c-42d0-49bc-88df-9e191dc42aa4" /><img width="256" height="256" alt="KB3D_IRF_BldgMdCrypt_A" src="https://github.com/user-attachments/assets/be528a3f-de15-4291-b46a-ac64347cb221" />
<img width="256" height="256" alt="KB3D_IRF_BldgMdMeltingShop_A" src="https://github.com/user-attachments/assets/2c87640a-9aba-49f9-89db-8f833450e2ca" />
<img width="256" height="256" alt="KB3D_IRF_PropAxe_B" src="https://github.com/user-attachments/assets/dce2febc-ec1a-4884-9974-46d86d899f86" />
<img width="256" height="256" alt="KB3D_IRF_PropBallista_A" src="https://github.com/user-attachments/assets/3a3fe1c1-0334-48c8-8a82-fccb2fb845f7" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmBorderHouse_A" src="https://github.com/user-attachments/assets/afcb54f9-b6e3-41f4-b9d8-bc7234f483c0" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmCoinage_A" src="https://github.com/user-attachments/assets/fd1f1f60-0f12-4dc6-825c-c6ca06d23d12" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmConstructionSite_A" src="https://github.com/user-attachments/assets/39be98ce-e426-4258-b998-971aef7f931d" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmMastersHut_A" src="https://github.com/user-attachments/assets/2d556d93-4d28-4adc-911f-995fa61b3a67" />
<img width="256" height="256" alt="KB3D_IRF_PropArrowQuiver_A" src="https://github.com/user-attachments/assets/19ca1082-79fd-4a2f-a6f8-7118ff035b1c" />
<img width="256" height="256" alt="KB3D_IRF_PropBanner_C" src="https://github.com/user-attachments/assets/c7f3c386-2d59-41f7-a35e-f28c1e2becb9" />
<img width="256" height="256" alt="KB3D_IRF_PropStoneTable_C" src="https://github.com/user-attachments/assets/1cf057ac-6423-49a1-aa0d-b1c5e0a0096f" />
<img width="256" height="256" alt="KB3D_IRF_PropBook_B" src="https://github.com/user-attachments/assets/140ede92-04d5-4239-9290-8a91b62faaf3" />
<img width="256" height="256" alt="KB3D_IRF_PropBooks_C" src="https://github.com/user-attachments/assets/0a27305e-63b0-4b2d-95c6-2e6070fdb89f" />
<img width="256" height="256" alt="KB3D_IRF_PropFireBowl_B" src="https://github.com/user-attachments/assets/7f030252-cd3b-42da-99d0-894a5fda626a" />
<img width="256" height="256" alt="KB3D_IRF_PropTrainHook_A" src="https://github.com/user-attachments/assets/6b29a352-de61-494e-8467-b62ab86bef75" />
<img width="256" height="256" alt="KB3D_IRF_PropLamp_A" src="https://github.com/user-attachments/assets/a427e664-7802-4f77-9dcc-1443d4e06cf4" />
