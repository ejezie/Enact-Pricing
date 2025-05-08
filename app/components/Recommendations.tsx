import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
  Chip,
  Box,
  Grid,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Business,
} from '@mui/icons-material';
import { Recommendation } from '../types';

interface RecommendationsProps {
  data: Recommendation[];
}

const getIcon = (type: string) => {
  switch (type) {
    case 'pricing':
      return <TrendingUp />;
    case 'strategy':
      return <Speed />;
    case 'competitor':
      return <Business />;
    default:
      return <TrendingUp />;
  }
};

const getImpactColor = (impact: string) => {
  switch (impact) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
};

export default function Recommendations({ data }: RecommendationsProps) {
  if (!data?.length) {
    return (
      <Typography variant="body1" color="text.secondary" align="center">
        No recommendations available
      </Typography>
    );
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper elevation={0} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Strategic Recommendations
          </Typography>
          <List>
            {data.map((recommendation, index) => (
              <ListItem
                key={index}
                alignItems="flex-start"
                sx={{
                  mb: 2,
                  backgroundColor: 'background.paper',
                  borderRadius: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ mt: 1 }}>
                  {getIcon(recommendation.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle1" component="span">
                        {recommendation.title}
                      </Typography>
                      <Chip
                        label={`Impact: ${recommendation.impact}`}
                        size="small"
                        color={getImpactColor(recommendation.impact)}
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ whiteSpace: 'pre-line' }}
                    >
                      {recommendation.description}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
    </Grid>
  );
} 