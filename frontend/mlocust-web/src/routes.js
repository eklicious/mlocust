/*!

=========================================================
* Paper Dashboard React - v1.3.0
=========================================================

* Product Page: https://www.creative-tim.com/product/paper-dashboard-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com)

* Licensed under MIT (https://github.com/creativetimofficial/paper-dashboard-react/blob/main/LICENSE.md)

* Coded by Creative Tim

=========================================================
* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
=========================================================
Forked for sample v0.0.1


*/
import UserPage from "views/User.js";

var routes = [
  {
    path: "/",
    name: "New Request",
    icon: "nc-icon nc-simple-add",
    component: UserPage,
    layout: "/",
  },
];
export default routes;
