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

*/
import React from "react";

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Table,
  Row,
  Col,
} from "reactstrap";

function Tables() {
  return (
    <>
      <div className="content">
        <Row>
          <Col md="12">
            <Card>
              <CardHeader>
                <CardTitle tag="h4">GKE Cluster Management</CardTitle>
              </CardHeader>
              <CardBody>
                <Table responsive>
                  <thead className="text-primary">
                    <tr>
                      <th>Status</th>
                      <th>Name</th>
                      <th>Region</th>
                      <th className="text-right">TTL</th>
                      <th className="text-right">Max Req/Sec</th>
                      <th className="text-right">Immediate Req/Sec</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><i className="fas  fa-circle text-danger" /></td>
                      <td>egkang-Dakota-Rice</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">36738</td>
                      <td className="text-right">36738</td>
                      <td className="text-right">36738</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-primary" /></td>
                      <td>egkang-Minerva-Hooper</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">23789</td>
                      <td className="text-right">23789</td>
                      <td className="text-right">23789</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-primary" /></td>
                      <td>egkang-Sage-Rodriguez</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">23789</td>
                      <td className="text-right">56142</td>
                      <td className="text-right">23789</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-primary" /></td>
                      <td>egkang-Philip-Chaney</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">23789</td>
                      <td className="text-right">38735</td>
                      <td className="text-right">56142</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-danger" /></td>
                      <td>egkang-Doris-Greene</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">56142</td>
                      <td className="text-right">63542</td>
                      <td className="text-right">98615</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-primary" /></td>
                      <td>egkang-Mason-Porter</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">56142</td>
                      <td className="text-right">78615</td>
                      <td className="text-right">98615</td>
                    </tr>
                    <tr>
                      <td><i className="fas  fa-circle text-primary" /></td>
                      <td>egkang-Jon-Porter</td>
                      <td>us-eas4-a</td>
                      <td className="text-right">56142</td>
                      <td className="text-right">98615</td>
                      <td className="text-right">56142</td>
                    </tr>
                  </tbody>
                </Table>
              </CardBody>
            </Card>
          </Col>
          
        </Row>
      </div>
    </>
  );
}

export default Tables;
