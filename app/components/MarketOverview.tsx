import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Link,
  Chip,
} from '@mui/material';
import { Product } from '../types';

interface MarketOverviewProps {
  data: Product[];
}

export default function MarketOverview({ data }: MarketOverviewProps) {
  if (!data?.length) {
    return (
      <Typography variant="body1" color="text.secondary" align="center">
        No data available
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} elevation={0}>
      <Table sx={{ minWidth: 650 }} aria-label="product table">
        <TableHead>
          <TableRow>
            <TableCell>Product Name</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Brand</TableCell>
            <TableCell>Seller</TableCell>
            <TableCell>Condition</TableCell>
            <TableCell>Location</TableCell>
            <TableCell>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((product, index) => (
            <TableRow
              key={index}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                  {product.title}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2" color="success.main" fontWeight="medium">
                  {product.price}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {product.brand || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {product.seller || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={product.condition || 'N/A'}
                  size="small"
                  variant="outlined"
                  color={
                    product.condition === 'New'
                      ? 'success'
                      : product.condition === 'Used'
                      ? 'warning'
                      : 'default'
                  }
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2" color="text.secondary">
                  {product.location || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell>
                <Link
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  underline="none"
                >
                  <Chip
                    label="View"
                    size="small"
                    color="primary"
                    clickable
                  />
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
} 