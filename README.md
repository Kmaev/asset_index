This repository contains a USD asset browser, a personal project I am currently developing.

The goal of this project is to create a tool that works across multiple DCC applications, allowing assets to be imported seamlessly into a stage.

One of the core features—currently merged into the main branch—is an asset check-in process for a production pipeline. As an example, the project uses a KitBash library.

The check-in process includes:
- Creating a library metadata catalog
- Generating a temporary USD stage for each asset
- Adding a light rig
- Computing the camera position and rotation for thumbnail rendering based on the calculated bounding box of the asset’s geometry
- Rendering thumbnails

This process prepares assets for ingestion into the asset browser and production pipeline.

Examples rendered thumbnails:

<img width="256" height="256" alt="KB3D_IRF_BldgMdPendulumForge_A" src="https://github.com/user-attachments/assets/74ce5455-ab18-40f1-b7b4-422ad6eac296" />
<img width="256" height="256" alt="KB3D_IRF_PropBallista_A" src="https://github.com/user-attachments/assets/5736ae7f-8659-4d21-9892-8c3fbd02bac6" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmCoinage_A" src="https://github.com/user-attachments/assets/3a16e30b-5cc4-4bf6-8c59-e75525a7f89b" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmConstructionSite_A" src="https://github.com/user-attachments/assets/e6e10eda-a1e3-4d06-b8b5-6f74419de90b" />
<img width="256" height="256" alt="KB3D_IRF_BldgSmMastersHut_A" src="https://github.com/user-attachments/assets/c36de7ad-b45a-4526-8555-20b815e18ada" />
<img width="256" height="256" alt="KB3D_IRF_PropArrowQuiver_A" src="https://github.com/user-attachments/assets/2adb1afc-b0f7-4df5-8d63-24c188a2afa7" />
<img width="256" height="256" alt="KB3D_IRF_PropAxe_A" src="https://github.com/user-attachments/assets/9dbc31b9-729a-483f-8d42-fca41290dab2" />
<img width="256" height="256" alt="KB3D_IRF_PropBanner_A" src="https://github.com/user-attachments/assets/06add7d2-111c-4e90-b145-ddae6e0d0320" />
<img width="256" height="256" alt="KB3D_IRF_PropBook_B" src="https://github.com/user-attachments/assets/4f600f3e-9149-41ce-b8ae-125fd3fb2729" />
<img width="256" height="256" alt="KB3D_IRF_PropBookShelf_A" src="https://github.com/user-attachments/assets/27bb4d30-93b2-4fb0-9706-3865aae22083" />
<img width="256" height="256" alt="KB3D_IRF_PropTable_A" src="https://github.com/user-attachments/assets/47391874-de5a-4c32-aaad-6d76fd13ce98" />
<img width="256" height="256" alt="KB3D_IRF_PropWallGem_A" src="https://github.com/user-attachments/assets/12138528-79bf-4317-97a6-7ce30fd63a36" />






